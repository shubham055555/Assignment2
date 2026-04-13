# ============================================================
# RISC-V Assembly — Factorial (Iterative Loop)
# ENCS302 Assignment 2 | RARS Simulator
# Computes 8! = 40320
# ============================================================
        .data
msg:    .string "8! = "
newline:.string "\n"

        .text
        .globl main
main:
        li      a1, 8           # n = 8
        li      a0, 1           # result = 1

        # Print label
        la      t0, msg
        mv      t1, a0          # save result
        mv      t2, a1          # save n
        li      a7, 4
        mv      a0, t0
        ecall
        mv      a0, t1
        mv      a1, t2

        call    factorial       # result in a0

        li      a7, 1           # print integer
        ecall
        la      a0, newline
        li      a7, 4
        ecall

        li      a7, 10          # exit
        ecall

# ── factorial(a1=n) → a0 ─────────────────────────────────
# Loop: result = 1; while n > 1 { result *= n; n-- }
# a0 = accumulator (result), a1 = n, t0 = temp
factorial:
        li      a0, 1           # result = 1
        blez    a1, fact_done   # n <= 0 → return 1
fact_loop:
        li      t0, 1
        ble     a1, t0, fact_done  # n <= 1 → done
        mul     a0, a0, a1      # result *= n
        addi    a1, a1, -1      # n--
        j       fact_loop
fact_done:
        ret
