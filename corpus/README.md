# Corpus

Five English translations of Indian texts, all old enough to be in the public domain. The pipeline reads every `.txt` file in this folder.

| File | Text | Edition |
|---|---|---|
| `shakuntala.txt` | Kalidasa, *Abhijnanasakuntalam* | Arthur W. Ryder's translation, from the Everyman's Library volume of Kalidasa's works |
| `meghaduta.txt` | Kalidasa, *Meghaduta* ("The Cloud Messenger") | H. H. Wilson's verse translation, 1813 edition |
| `gitanjali.txt` | Rabindranath Tagore, *Gitanjali* | 1912 English version |
| `panchatantra.txt` | The *Panchatantra* | Arthur W. Ryder's translation, 1925 |
| `jataka.txt` | The *Jataka*, stories of the Buddha's former births | E. B. Cowell's edition (Cambridge University Press) |

## About the text files

These came from scanned books on the Internet Archive and Google Books, so they are OCR text. Expect misread characters, running page headers and library stamps near the start of each file. I did not clean them by hand. This affects the extraction a little, because a garbled word cannot be matched, and it is one reason the list of names is not complete.

I used English translations because a 7B local model reads English much more reliably than Sanskrit or Pali. The translations are the translators' work and the choices they made (for example *pard*, an old English word for leopard) show up in the extracted names.
