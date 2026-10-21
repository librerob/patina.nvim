# Design notes

Patina starts with copper and verdigris. Dark mode puts warm accents on green-black ink; light mode puts terracotta and teal on bone paper.

Dark strings use a softer brass, with slightly quieter mint and blue accents. Light strings use warm brown-brass instead of olive. Comments remain readable, and punctuation sits between comments and operators in luminance.

Light-mode keywords are close in luminance to the other accents. Control flow therefore gets a modest weight difference: conditionals, loops, returns, and exceptions are bold. Function declarations and the rest of the keyword family remain normal weight. The option can be disabled.

Selection is an interaction state, with its own text and background colors. Its surface contrasts with the editor background by more than 3:1 in both variants; selected text exceeds 5:1. Syntax colors are intentionally replaced inside the selection. Reference highlights use a quieter surface and an underline so the syntax can remain visible.

Completion has a different requirement: label matches, kind text, and source labels may all keep their own foregrounds. A quiet teal-gray selected surface keeps these readable. Matches get an underline as well as color. Dark-on-teal inverted menu selections were removed because plugin item foregrounds can override the selected text color.

Errors and warnings also have underlines, undercurls, signs, or severity text, depending on the Neovim display being used. Hue differences alone are not a guarantee of accessibility. No universal colorblind-safe certification or numerical design score is claimed.

Borders, whitespace, and passive line numbers are deliberately quieter than ordinary text. They are excluded from the 4.5:1 text contrast contract. The light line numbers were strengthened from the initial palette.
