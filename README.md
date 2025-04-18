# Congruence Closure

This project is an interactive tool that implements the **Congruence Closure algorithm** — supporting SMT-style input, incremental updates, disequality assertions, step-by-step explanation, and multiple interfaces (Web GUI, CLI, and Desktop GUI).

---

## Features

- SMT2-style expression parsing (e.g., `(assert (= a b))`)
- Function currying and flattening for uniform term structure
- Handles equality and disequality: `(assert (= a b))`, `(assert (not (= a b)))`
- UI support to:
  - Add assertions
  - Explain relationships
  - Upload `.smt2` files
  - Show final equivalence classes
  - Pop the last equation
- Supports both constant and function terms (e.g., `f(a)`, `s(p(x))`)
- Web-based Flask UI and Tkinter-based desktop GUI
- Extendable to show proof traces and class visualizations

---

## Project Structure



---

## Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/anshulj07/CongruenceClosure
cd CongruenceClosure
````
### 2. Setup Virtual Environment 
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
````
### 3. Run the Web App
```bash
python3 app.py
````

## Input Examples

### Equality
```bash
(assert (= a b))
(assert (= f(a) f(b)))
````

### Disequality
```bash
(assert (not (= a z)))
````

### Nested Functions:
```bash
(assert (= s(p(x)) x))
````

## Pop/Undo Support
Clicking "Pop" removes the most recently added equation and rebuilds the equivalence structure. Useful for undoing mistakes during interactive input.

### Explanation Support
You can input:
```bash
a c
````
or:

```bash
(f a) (f c)
````

and the system will:
#### 1. Show whether they are equivalent

#### 2. Display a basic explanation (proof trace in progress)

## Uploading .smt2
### Upload a file containing assertions like:
````bash
(assert (= a b))
(assert (= b c))
(assert (= c d))
(assert (not (= a z)))
(assert (= f(a) f(b)))
(assert (= s(p(x)) x))
(assert (= p(s(y)) y))
````

## Credits

> **Developed by Anshul Jain and Yogalakshmi Venkatesan**  