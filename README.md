#Blink(1) Apps

This is a collection of the tools I created for my blink(1) devices.

## old distros
Most of them use [blink1-python](https://github.com/todbot/blink1-python) so you should prepare your system as detailed [here](https://github.com/todbot/blink1-python#installation) and [here](https://github.com/todbot/blink1-python#os-specific-notes).

## new distros like Ubuntu 24

On newer distributions like Ubuntu 24 pip will not globally install packages. They need to be either installed from official apt packages (externally managed) or inside a virtual environment.

Since the blink1 python package is not provided by apt, a venv needs to be created to use these apps.

A shell script `install_venv.sh` is provided to do this for you.

You also need to copy the provided udev rules `51-blink1.rules` to `/etc/udev/rules.d/` and the run `sudo udevadm control --reload-rules` for the blink(1) devices to be accessible. (As per [github.com/todbot/Blink1Control2](https://github.com/todbot/Blink1Control2?tab=readme-ov-file#linux)

