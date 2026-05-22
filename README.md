# Hill Cipher  A Linear Algebra Exercise

A from scratch implementation of the **Hill cipher** in Python, built as a hands on excuse to work through the linear algebra ideas that make it tick matrix multiplication, determinants, the adjugate formula, and the modular inverse of a matrix.

The cipher itself is broken by modern standards. That's not the point. The point is that every step of encryption, decryption, and even cryptanalysis is a clean, self contained piece of linear algebra over a finite ring  and writing it out by hand is one of the most concrete ways to internalize what those operations actually *do*.

---

## What the Hill cipher is

Invented by Lester S. Hill in 1929, the Hill cipher is the first practical polygraphic cipher: it encrypts blocks of letters at a time using matrix multiplication, rather than one letter at a time.

The whole scheme reduces to a single equation:

```
C ≡ K · P   (mod 26)
```

where:

| Symbol | Meaning |
|--------|---------|
| `P` | plaintext block, as a column vector of letter indices (a=0, b=1, ..., z=25) |
| `K` | the secret key  an `n × n` matrix, invertible modulo 26 |
| `C` | ciphertext block, also a column vector mod 26 |
| `n` | block size (this project uses `n = 2`) |

Decryption is just the inverse linear map:

```
P ≡ K⁻¹ · C   (mod 26)
```

The catch  and the whole reason the project gets interesting  is that `K⁻¹` is taken in **modular arithmetic**, not over the real numbers. That single twist forces you to actually understand what a matrix inverse *means*.

---

## The linear algebra concepts being exercised

This project deliberately reaches past `numpy.linalg.inv` and rebuilds the pieces, because the goal is understanding, not shortcuts.

### 1. Linear transformations over a finite ring
Multiplying by `K` is a linear map from `(ℤ/26ℤ)ⁿ` to itself. Every property you know from `ℝⁿ`  linearity, invertibility, the role of the determinant  still applies, but the underlying field is replaced by integers mod 26. Working in this setting makes "the determinant tells you whether the map is invertible" feel like a real, operational statement rather than a textbook line.

### 2. The adjugate (classical adjoint) formula
For a 2×2 (or any `n × n`) matrix, the inverse can be written as:

```
A⁻¹ = (1 / det A) · adj(A)
```

Over the reals, you'd just call `np.linalg.inv`. Over `ℤ/26ℤ`, division isn't a thing  so you have to compute the adjugate explicitly and then replace `1 / det A` with the **modular multiplicative inverse** of the determinant.

### 3. Modular inverses, GCD, and Bézout's identity
A matrix is invertible mod 26 if and only if `gcd(det(K), 26) = 1`. That's where the bridge between **number theory** and **linear algebra** shows up: the existence of the inverse depends on the determinant being coprime with the modulus. The code computes `det(K)⁻¹ (mod 26)` directly to drive that point home.

### 4. Cryptanalysis as solving a linear system
The most striking demonstration of "linear maps are easy to invert" comes from the attacker's view. Given any two matching plaintext/ciphertext blocks, an attacker stacks them into square matrices `P` and `C` and solves:

```
K = C · P⁻¹   (mod 26)
```

One matrix inversion mod 26 is all it takes to recover the key. This is the cipher's fatal flaw and, more interestingly, a clean illustration of why **any** purely linear cryptosystem is doomed: linearity is exactly the property that makes systems solvable.

---

## Repository layout

```
.
├── hillCipherForward.ipynb   Worked-through notebook: every step shown explicitly
├── hill_cipher.py            Clean, reusable module mirroring the notebook
├── requirements.txt          Just numpy
└── README.md                 You are here
```

The notebook is the "show your work" version  it builds the cipher up cell by cell, prints intermediate matrices, and ends with the attacker demonstration. The Python module is the same logic reorganized into small named functions you'd actually import.

---

## Running it

```bash
pip install -r requirements.txt
python hill_cipher.py
```

Expected output:

```
Original : Hello this is hill cipher encryption project
Encrypted: hiozvttcayxtftngrnhilctktyyvoigxpanmlv
Decrypted: hellothisishillcipherencryptionproject
Key * KeyInverse (mod 26):
[[1 0]
 [0 1]]
Key recovered by attacker:
[[3 3]
 [2 5]]
```

The last block is the punch line: the attacker, knowing only the first four plaintext/ciphertext letters, reconstructs the original key matrix exactly.

---

## API at a glance

The implementation is wrapped in a single class, `HillCipherEncryption`, which holds the key matrix and exposes each step of the cipher as its own method, so every public name maps directly to a piece of linear algebra.

```python
import numpy as np
from hill_cipher import HillCipherEncryption

key = np.array([[3, 3],
                [2, 5]])

cipher = HillCipherEncryption(key)

ciphertext = cipher.encrypt("hello this is hill cipher", key)
plaintext  = cipher.decrypt(ciphertext, key)

key_inv   = cipher.matrix_mod_inverse(key)                # K⁻¹ mod 26
recovered = cipher.recover_key(P_block, C_block)          # known-plaintext attack
```

Method-by-method:

| Method | Linear-algebra operation |
|--------|--------------------------|
| `preprocess_text` | Normalize input and pad so it splits evenly into blocks |
| `text_to_matrix` / `matrix_to_text` | Encode letters as a numeric matrix over `ℤ/26ℤ` and back |
| `apply_key` | The linear map itself: `K · X (mod 26)` |
| `mod_inverse` | Modular multiplicative inverse of an integer mod 26 |
| `matrix_mod_inverse` | `K⁻¹ (mod 26)` via the adjugate formula |
| `encrypt` / `decrypt` | The forward and inverse linear transformations end-to-end |
| `recover_key` | Cryptanalysis: solve `K = C · P⁻¹ (mod 26)` from a known pair |

Every method is short, single-purpose, and named after the operation it performs, so the source reads like a transcript of the math.

---

## Why bother with a broken cipher?

Because the Hill cipher is the simplest non trivial cryptosystem where the *entire* lifecycle key generation, encryption, decryption, and a complete break  fits inside one corner of an undergraduate linear algebra course. Building it from first principles forces you to confront:

- what a matrix inverse really *is* (not just `inv(A)`),
- why determinants matter beyond a number on a homework sheet,
- how modular arithmetic changes the rules,
- and why linearity is a liability the moment an adversary gets one matching pair of inputs and outputs.

That last point  that the same property making the cipher elegant is what makes it fall apart  is the whole reason modern cryptography spends so much energy introducing controlled non-linearity (S-boxes, ARX, etc.). The Hill cipher is the cleanest possible illustration of *why*.
