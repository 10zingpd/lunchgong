# lunchgong

Lunch reminder - built on Viam!

## Language

**Python 3.14+**

## Architecture TLDR

This is a **Viam module** (custom robot component) that rings a physical gong when triggered via Viam's command interface.

**Key Components:**
- **Viam Generic Component** (`10zing:generic:gong`) - Custom component that wraps servo and board control
- **Servo Motor** - Physically strikes the gong with a back-and-forth motion
- **GPIO Board** - Controls a pin (GPIO 11) that likely activates a solenoid or additional mechanism
- **Command Interface** - Receives commands via Viam's `do_command` API, checks if a subteam is mentioned in the command text, and triggers the gong sequence

**Flow:**
1. Module receives a command with text via Viam's `do_command` interface
2. Checks if the configured `subteam` is mentioned in the command text
3. If triggered:
   - Sets GPIO pin 11 high
   - Moves servo through sequence: 110° → 90° → 110° (striking motion)
   - Sets GPIO pin 11 low
4. Returns success/failure status

**Build & Deploy:**
- Uses `uv` for Python package management
- Packaged as `module.tar.gz` via Makefile
- Registered in Viam module registry as `10zing:lunchgong`
- Entrypoint: `run.sh` → `uv run module.py`
