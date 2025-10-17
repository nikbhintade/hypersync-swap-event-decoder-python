import asyncio
import json
from typing import List, Any

import hypersync
from eth_abi import decode
from eth_utils import remove_0x_prefix, to_checksum_address


def normalize_topics(raw_topics: Any) -> List[str]:
    """
    Accepts:
      - a Python list of topics (['0x...', '0x...', ...])
      - a JSON string like '["0x...", "0x..."]'
      - a concatenated hex string '0x{topic0}{topic1}{topic2}' (rare)
    Returns a list of '0x...' topics.
    """
    if raw_topics is None:
        return []

    # If already a list, assume it's good
    if isinstance(raw_topics, list):
        return raw_topics

    # If it's a string, try to parse common formats
    if isinstance(raw_topics, str):
        s = raw_topics.strip()

        # try JSON list string
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass

        # if a single hex string - possibly a concatenation of 32-byte topics
        # strip 0x then split every 64 hex chars
        if s.startswith("0x"):
            s_no = remove_0x_prefix(s)
            if len(s_no) % 64 == 0:
                chunks = []
                for i in range(0, len(s_no), 64):
                    chunks.append("0x" + s_no[i : i + 64])
                return chunks

        # As a final fallback: return the single string
        return [s]

    # Anything else -> empty
    return []


def topic_to_address(topic_hex: str) -> str:
    """
    Recover address from indexed address topic (topics store keccak/padded values).
    The address is right-aligned in the 32-byte topic (last 20 bytes).
    """
    if not topic_hex:
        return None
    # ensure hex without 0x
    clean = remove_0x_prefix(topic_hex)
    if len(clean) < 40:
        return None
    addr_hex = "0x" + clean[-40:]
    try:
        return to_checksum_address(addr_hex)
    except Exception:
        # if checksum fails, return lowercase fallback
        return addr_hex.lower()


async def main():
    client = hypersync.HypersyncClient(hypersync.ClientConfig())

    eth_rai_swap_pool = "0x3e47D7B7867BAbB558B163F92fBE352161ACcb49"

    event_topic_0 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"

    start_block = 0
    end_block = 20_333_826

    query = hypersync.preset_query_logs_of_event(
        eth_rai_swap_pool, event_topic_0, start_block, end_block
    )

    print("Running the query...")
    res = await client.get(query)

    # res.data.logs is usually a list of Log objects
    logs = getattr(res.data, "logs", []) or []
    print(f"Fetched {len(logs)} Swap logs")

    if logs:
        print("Example log (first one):")
        first_log = logs[0]
        # Fallback: try __dict__, else dir()
        if hasattr(first_log, "__dict__"):
            print(first_log.__dict__)
        else:
            # Print available attributes and their values
            for attr in dir(first_log):
                # skip builtins
                if attr.startswith("_"):
                    continue
                try:
                    val = getattr(first_log, attr)
                    print(f"{attr}: {val}")
                except Exception as e:
                    print(f"{attr}: <error reading: {e}>")
    else:
        print("No logs returned.")


    decoded_events = []

    for log in logs:
        try:
            # Access attributes safely (Log is an object, not a dict)
            raw_topics = getattr(log, "topics", None)
            topics = normalize_topics(raw_topics)

            # topics[0] is topic0 (event sig), indexed params follow
            # For Swap event: indexed sender (topic1) and to (topic2)
            sender = topic_to_address(topics[1]) if len(topics) > 1 else None
            to = topic_to_address(topics[2]) if len(topics) > 2 else None

            raw_data = getattr(log, "data", "") or ""
            data_hex = remove_0x_prefix(raw_data)
            data_bytes = bytes.fromhex(data_hex) if data_hex else b""

            # Non-indexed args in this Swap event: amount0In, amount1In, amount0Out, amount1Out
            if data_bytes:
                amounts = decode(
                    ["uint256", "uint256", "uint256", "uint256"], data_bytes
                )
            else:
                amounts = (0, 0, 0, 0)

            block_number = getattr(log, "block_number", None)
            # transaction hash may be named transaction_hash or transactionHash depending on library
            tx_hash = getattr(log, "transaction_hash", None) or getattr(
                log, "transactionHash", None
            )

            event_obj = {
                "block_number": block_number,
                "tx_hash": tx_hash,
                "address": getattr(log, "address", None),
                "sender": sender,
                "to": to,
                "amount0In": str(amounts[0]),
                "amount1In": str(amounts[1]),
                "amount0Out": str(amounts[2]),
                "amount1Out": str(amounts[3]),
                # keep the original raw fields for debugging
                "raw_topics": topics,
                "raw_data": raw_data,
            }

            decoded_events.append(event_obj)

        except Exception as e:
            # Keep going if a single log fails
            print(f"Error decoding log: {e}")
            continue

    # Write decoded events to JSON
    with open("swap_events.json", "w") as f:
        json.dump(decoded_events, f, indent=2)

    print(f"Saved {len(decoded_events)} decoded Swap events to swap_events.json")


if __name__ == "__main__":
    asyncio.run(main())
