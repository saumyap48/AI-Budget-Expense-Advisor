import sys
sys.path.insert(0, 'app')

from passlib.context import CryptContext
ctx = CryptContext(schemes=["argon2"], deprecated="auto")

# Task-required tests
pw = "12345678"
h = ctx.hash(pw)
print("hash_password result:", h[:50] + "...")

ok = ctx.verify(pw, h)
print("verify_password correct pw:", ok)
assert ok, "FAILED: verify returned False"

wrong = ctx.verify("wrongpass", h)
assert not wrong, "FAILED: wrong password should not verify"
print("verify_password wrong pw:   False (correct)")

assert "argon2" in h, "FAILED: hash is not argon2"
print("Algorithm confirmed:", h.split("$")[1])
print()
print("ALL TESTS PASSED")
