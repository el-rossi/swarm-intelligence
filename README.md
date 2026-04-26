# Swarm Intelligence

## Requirements
- Python 3.12 (used 3.12.10)
- pip

---

## Environment Setup

### 1. Clone the repository
```sh
git clone https://github.com/el-rossi/swarm-intelligence.git
cd swarm-intelligence
```

### 2. Create a virtual environment
```sh
python -m venv .venv
```
> If you have multiple Python versions installed, use:
> ```sh
> py -3.12 -m venv .venv
> ```

### 3. Activate the virtual environment
| Platform | Command |
|----------|---------|
| Windows  | `.venv\Scripts\activate` |
| Linux    | `source .venv/bin/activate` |

> To exit the virtual environment, run `deactivate`.

### 4. Install dependencies
```sh
pip install -r requirements.txt
pip install solara
```
> **Note:** Some environments may require adding `starlette<0.37` and `altair==5.3.0` to `requirements.txt` if errors occur during installation.

---

## Running the Project

From inside the `swarm-intelligence` folder:

### 1. Activate the virtual environment (if not already active)
See [3. Activate the virtual environment](#3-activate-the-virtual-environment).

### 2. Run the app
```sh
cd project-1
solara run app.py
```
