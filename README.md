# Hypersync Swap Event Decoder

This script fetches and decodes **Swap** events from the Ethereum blockchain using [Hypersync](https://docs.envio.dev/docs/HyperSync/overview).
It queries logs for a specific pool and event topic, decodes event data (addresses and amounts), and saves the results to a JSON file.

---

## 🧰 Requirements

-   Python **3.10+**
-   Recommended: run inside a virtual environment

---

## ⚙️ Setup

```bash
# 1. Clone this repo or copy main.py into a folder
git clone https://github.com/nikbhintade/hypersync-swap-event-decoder-python.git
cd hypersync-swap-event-decoder-python

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # On Windows: env\Scripts\activate

# 3. Install dependencies
pip install hypersync eth-abi eth-utils
```

---

## ▶️ Run the Script

```bash
python main.py
```

This will:

-   Connect to HyperSync
-   Fetch all Swap event logs for the specified pool
-   Save results to `swap_events.json`

---

## 📄 Output

A `swap_events.json` file is created containing decoded event data, for example:

```json
[
    {
        "block_number": 19690320,
        "tx_hash": "0xb501bb8...",
        "address": "0x3e47...",
        "sender": "0x3328...",
        "to": "0x0f89...",
        "amount0In": "2228...",
        "amount1In": "9999..",
        "amount0Out": "9999..",
        "amount1Out": "9999..",
        "raw_topics": [
            "0xd78ad...",
            "0x00000...",
            "0x00000...",
            null
        ],
        "raw_data": "0x000000000..."
    }
]
```

---

## 🧩 Notes

-   You can modify `eth_rai_swap_pool`, `event_topic_0`, and block range (`start_block`, `end_block`) in `main.py` to query different pools or events.
-   Any decoding errors are caught and logged so one faulty log doesn’t stop execution.
