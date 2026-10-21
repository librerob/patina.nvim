# Design notes

Verdelle starts with copper and verdigris. Dark mode puts warm accents on green-black ink; light mode puts terracotta and teal on bone paper.

Dark strings use a softer brass, with slightly quieter mint and blue accents. Light strings use warm brown-brass instead of olive. Comments remain readable, and punctuation sits between comments and operators in luminance.

Light-mode accents now have a deliberate lightness hierarchy: deep terracotta keywords, plum constants, blue types, then teal functions and brass strings. The last two remain close in lightness but sit on different warm/cool hue families. Bold control flow is off by default and can be enabled; it supplements the colors rather than carrying the hierarchy. Function declarations and the rest of the keyword family retain normal weight.

The revision was measured under normal vision and the published Machado protan, deutan, and tritan simulations at ten severity levels. The weakest light pair improved from 4.51 to 9.22 CIEDE2000. Dark was retained, including the copper/mint pair: it was already well separated in these simulations. The remaining closest dark pair is function/type under full tritan simulation. [Method, full report, and limitations](COLORVISION.md).

Selection is an interaction state, with its own text and background colors. Its surface contrasts with the editor background by more than 3:1 in both variants; selected text exceeds 5:1. Syntax colors are intentionally replaced inside the selection. Reference highlights use a quieter surface and an underline so the syntax can remain visible.

Completion has a different requirement: label matches, kind text, and source labels may all keep their own foregrounds. A quiet teal-gray selected surface keeps these readable. Matches get an underline as well as color. Dark-on-teal inverted menu selections were removed because plugin item foregrounds can override the selected text color.

Errors and warnings also have underlines, undercurls, signs, or severity text, depending on the Neovim display being used. Hue differences alone are not a guarantee of accessibility. No universal colorblind-safe certification or numerical design score is claimed.

Borders, whitespace, and passive line numbers are deliberately quieter than ordinary text. They are excluded from the 4.5:1 text contrast contract. The light line numbers were strengthened from the initial palette.
