# ============================================================
# RISC-V Assembly — String Reversal
# ENCS302 Assignment 2 | RARS Simulator
# Reverses "HELLO" → "OLLEH"
# ============================================================
        .data
src:    .string "HELLO"
buf:    .space  16
msg1:   .string "Original : "
msg2:   .string "\nReversed : "
newline:.string "\n"

        .text
        .globl main
main:
        # Print original string
        la      a0, msg1
        li      a7, 4
        ecall
        la      a0, src
        ecall

        # Find length of src
        la      t0, src         # t0 = ptr to src
        li      t1, 0           # t1 = length counter
len_loop:
        lb      t2, 0(t0)       # load byte
        beqz    t2, len_done    # null terminator?
        addi    t0, t0, 1
        addi    t1, t1, 1
        j       len_loop
len_done:
        # t1 = length, t0 points past last char

        la      t3, buf         # t3 = write pointer (dst)
        la      t4, src         # t4 = read from end of src
        add     t4, t4, t1
        addi    t4, t4, -1      # t4 → last char of src

rev_loop:
        blez    t1, rev_done    # if remaining == 0, stop
        lb      t5, 0(t4)       # load char from end
        sb      t5, 0(t3)       # store to buf
        addi    t4, t4, -1      # move src ptr back
        addi    t3, t3, 1       # move dst ptr forward
        addi    t1, t1, -1
        j       rev_loop
rev_done:
        sb      zero, 0(t3)     # null-terminate buf

        # Print reversed string
        la      a0, msg2
        li      a7, 4
        ecall
        la      a0, buf
        ecall
        la      a0, newline
        ecall

        li      a7, 10          # exit
        ecall
