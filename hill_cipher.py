"""
Hill Cipher encryption and decryption using a 2x2 key matrix over mod 26.

Mirrors the logic in hillCipherForward.ipynb but organized into small,
reusable functions.
"""

from math import gcd
import numpy as np

class HillCipherEncryption:
    mod = 26
    def __init__(self, key_matrix: np.ndarray) -> None:
        self.key_matrix = key_matrix
        self.LETTER_TO_NUM = {chr(ord("a") + i): i for i in range(26)}
        self.NUM_TO_LETTER = {i: ch for ch, i in self.LETTER_TO_NUM.items()}


    def __preprocess_text(self,text: str, block_size: int = 2, pad_char: str = "x") -> str:
        cleaned = text.lower().replace(" ", "")
        while len(cleaned) % block_size != 0:
            cleaned += pad_char
        return cleaned

    # ---------------------------------------------------------------------------
    # Text <-> numeric matrix helpers
    # ---------------------------------------------------------------------------

    def __text_to_matrix(self,text: str, block_size: int = 2) -> np.ndarray:
        # Split into block_size-sized chunks, e.g. "hello" -> ["he","ll","ox"]
        chunks = [text[i:i + block_size] for i in range(0, len(text), block_size)]
        # Map each letter to its numeric value, then transpose so columns = blocks
        numeric = np.array([[self.LETTER_TO_NUM[ch] for ch in chunk] for chunk in chunks])
        return numeric.T


    def __matrix_to_text(self,matrix: np.ndarray) -> str:
        result = []
        for col_index in range(matrix.shape[1]):
            for value in matrix[:, col_index]:
                result.append(self.NUM_TO_LETTER[int(value) % self.mod])
        return "".join(result)


    # ---------------------------------------------------------------------------
    # Modular-arithmetic helpers needed to invert the key matrix
    # ---------------------------------------------------------------------------
    def __mod_inverse(self,n: int, mod: int = mod) -> int:
        """
        Find the modular inverse of n modulo `mod`, i.e. the integer x such that
        (n * x) % mod == 1. Brute-force search is fine for small moduli like 26.
        """
        n = int(n) % mod
        for x in range(1, mod):
            if (n * x) % mod == 1:
                return x
        raise ValueError(f"No modular inverse exists for {n} mod {mod}")


    def __matrix_mod_inverse(self,matrix: np.ndarray, mod: int = mod) -> np.ndarray:
        """
        Formula:  A^-1 (mod m) = det(A)^-1 * adj(A)  (mod m)
        where adj(A) = det(A) * inv(A) is the classical adjugate matrix.
        Requires gcd(det(A), m) == 1; otherwise the inverse does not exist.
        """
        det = round(float(np.linalg.det(matrix)))
        if gcd(det % mod, mod) != 1:
            raise ValueError("Key matrix is not invertible mod 26 (det not coprime with 26)")

        adjugate = (np.linalg.inv(matrix) * det) % mod
        inverse = (self.__mod_inverse(det, mod) * adjugate) % mod
        return np.round(inverse).astype(int) % mod


    # ---------------------------------------------------------------------------
    # Core Hill-cipher encryption / decryption
    # ---------------------------------------------------------------------------
    def __apply_key(self,key: np.ndarray, numeric_matrix: np.ndarray) -> np.ndarray:
        return (key @ numeric_matrix) % self.mod


    def encrypt(self,plaintext: str, key: np.ndarray) -> str:
        block_size = key.shape[0]
        prepared = self.__preprocess_text(plaintext, block_size)
        numeric = self.__text_to_matrix(prepared, block_size)
        encrypted_numeric = self.__apply_key(key, numeric)
        return self.__matrix_to_text(encrypted_numeric)


    def decrypt(self,ciphertext: str, key: np.ndarray) -> str:
        block_size = key.shape[0]
        key_inv = self.__matrix_mod_inverse(key)
        numeric = self.__text_to_matrix(ciphertext, block_size)
        decrypted_numeric = self.__apply_key(key_inv, numeric)
        return self.__matrix_to_text(decrypted_numeric)


    # ---------------------------------------------------------------------------
    # Attacker's view — known-plaintext attack
    #
    # The Hill cipher is a linear transformation: C = K · P (mod 26).
    # If an attacker captures even one plaintext block P and its matching
    # ciphertext block C, they can solve for the key directly:
    #
    #     K = C · P^-1 (mod 26)
    #
    # Concatenating enough blocks to form a square, invertible P matrix is all
    # it takes. That is the cipher's fatal weakness: linearity makes it trivial
    # to break under any known-plaintext exposure.
    # ---------------------------------------------------------------------------
    def recover_key(self,plaintext_block: np.ndarray, ciphertext_block: np.ndarray) -> np.ndarray:
        plaintext_inv = self.__matrix_mod_inverse(plaintext_block)
        return (ciphertext_block @ plaintext_inv) % self.mod



def main() -> None:
    raw_text = "Hello this is hill cipher encryption project"
    key = np.array([[3, 3], [2, 5]])

    cipher = HillCipherEncryption(key)

    encrypted = cipher.encrypt(raw_text, key)
    decrypted = cipher.decrypt(encrypted, key)

    print(f"Original : {raw_text}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")


    # Attacker's view: with two known plaintext blocks ("he", "ll") and their
    # matching ciphertext blocks ("hi", "oz"), the key falls out of one
    # matrix inversion mod 26.
    plaintext_block = np.array([[7, 11], [4, 11]])   # columns: "he", "ll"
    ciphertext_block = np.array([[7, 14], [8, 25]])  # columns: "hi", "oz"
    recovered = cipher.recover_key(plaintext_block, ciphertext_block)
    print(f"Key recovered by attacker:\n{recovered}")


if __name__ == "__main__":
    main()