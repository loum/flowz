# Setup the development environment

!!! note
    At this point, it is assumed that you have already forked a copy of [Dagster](https://github.com/loum/dagster){target="blank"}.

## Prerequisites

- [GNU make](https://www.gnu.org/software/make/manual/make.html){target="blank"}.
- Python 3 Interpreter. [We recommend installing pyenv](https://github.com/pyenv/pyenv){target="blank"}.
- [Docker](https://www.docker.com/){target="blank"}.
- To run local PySpark you will need [OpenJDK 11](https://openjdk.java.net/install/){target="blank"}.

!!! note
    [Makester](https://loum.github.io/makester/){target="blank"} is used as the Integrated Developer Platform.

### (macOS Users only) upgrading GNU `make`
Follow [these notes](https://loum.github.io/makester/macos/#upgrading-gnu-make-macos){target="blank"} to get [GNU make](https://www.gnu.org/software/make/manual/make.html){target="blank"}.

## Build the local virtual environment

Get the code and change into the top level `git` project directory. The following  uses the `dagster` project
repository as an example:
``` sh
git clone https://github.com/loum/dagster.git && cd dagster
```

!!! note
    Run all commands from the top-level directory of the `git` repository.

For first-time setup, get the [Makester project](https://github.com/loum/makester.git):
``` sh
git submodule update --init
```

Initialise the environment:
``` sh
make pristine
```

Run the test harness to validate your local environment setup:
``` sh
make tests
```
