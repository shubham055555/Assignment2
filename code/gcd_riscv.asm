# ============================================================
# RISC-V Assembly — GCD (Euclidean Algorithm)
# ENCS302 Assignment 2 | RARS Simulator
# Computes GCD(48, 18) → expected: 6
# ============================================================
        .data
msg_a:  .string "GCD("
msg_b:  .string ", "
msg_c:  .string ") = "
newline:.string "\n"

        .text
        .globl main
main:
        li      a0, 48          # a = 48
        li      a1, 18          # b = 18

        # Print "GCD("
        la      a2, msg_a
        mv      a3, a0          # save a
        mv      a4, a1          # save b
        li      a7, 4
        mv      a0, a2
        ecall
        li      a7, 1
        mv      a0, a3
        ecall
        la      a0, msg_b
        li      a7, 4
        ecall
        li      a7, 1
        mv      a0, a4
        ecall
        la      a0, msg_c
        li      a7, 4
        ecall

        mv      a0, a3          # restore a
        mv      a1, a4          # restore b
        call    gcd             # result in a0

        li      a7, 1           # print integer result
        ecall
        la      a0, newline
        li      a7, 4
        ecall

        li      a7, 10          # exit
        ecall

# ── gcd(a0, a1) → a0 ─────────────────────────────────────
# Uses Euclidean algorithm: while b != 0 { t=b; b=a%b; a=t }
# Registers: a0=a, a1=b, t0=temp
gcd:
        beqz    a1, gcd_done    # if b == 0, return a
gcd_loop:
        rem     t0, a0, a1      # t0 = a % b
        mv      a0, a1          # a  = b
        mv      a1, t0          # b  = t0
        bnez    a1, gcd_loop    # if b != 0, continue
gcd_done:
        ret                     # return a0 (= GCD)
