; Great Battle Gaiden 2 English patch. Applied by tools/build.py to a 2 MB copy (banks $28-$3F are free, 0xFF).
; Text engine notes: docs/re/text.md.
lorom

!BODY_BANK = $0028              ; must match tools/build.py BODY_BANK / BODY_TABLE
!BODY_TABLE = $8000
!CODE = $3F8000                 ; patch code, last bank of the 2 MB image

; ---------------------------------------------------------------------------------------------------------------
; Message bodies move to bank $28: the body pointer table ($1A:C1EC) is rebuilt at $28:8000 by the build.
; Both readers (page-clear pre-pass and the main printer) load the table address + bank as immediates.
org $01850B
    db $A9 : dw !BODY_TABLE     ; lda #table
org $018510
    db $A9 : dw !BODY_BANK      ; lda #bank
org $0186A2
    db $A9 : dw !BODY_TABLE
org $0186A7
    db $A9 : dw !BODY_BANK

; ---------------------------------------------------------------------------------------------------------------
; Line pitch 1 row instead of 2: Japanese needed a row above each line for dakuten; English doesn't, so a
; 2-line box holds 4 lines. Headers start one row higher (build.py), and the encoder adds a leading {n} plus
; blank rows between lines when the page fits the original 2-row spacing.
org $01855F
    db $69 : dw $0020           ; pre-pass newline: adc #$20 (was #$40)
org $0186D4
    db $69 : dw $0020           ; printer newline: adc #$20 (was #$40)
org $018594
    db $E9 : dw $0000           ; pre-pass cleared the dakuten row above each line (sbc #$20): with the first
                                ; line on that row it would wipe the box border, so clear the line row only

; ---------------------------------------------------------------------------------------------------------------
; The page-clear pre-pass counted control bytes as characters, so a line with {wait:XX} cleared tiles past its
; end (over the box border once English fills the width). Count printable bytes only. A = byte + 3 here.
org $01854C
    jml prepass_count

org !CODE
prepass_count:
    cmp #$FC                    ; byte < $F9: a character
    bcc .char
    cmp #$FF                    ; byte $FC {wait:XX}: also skip its argument
    bne .done
    rep #$20
    inc $18
    sep #$20
    bra .done
.char:
    inc $1A
.done:
    jml $018538
