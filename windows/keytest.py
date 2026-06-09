#!/usr/bin/env python3
"""
Testeur de touches.

Affiche chaque evenement clavier capte par pynput (le meme moteur que le
gestionnaire multi-ecrans). Sert a :
  - verifier que l'ecoute des raccourcis fonctionne sur ce PC ;
  - voir ce qu'envoient les touches macro G1..G5 du Logitech G915 (rien par
    defaut : il faut les configurer dans Logitech G HUB pour qu'elles emettent
    une vraie touche, par ex. F13..F20).

Lancez, puis pressez : Ctrl+Maj+Home, Ctrl+Maj+Fin, puis G1, G2, G3...
Echap (ou Ctrl+C) pour quitter.
"""

from pynput import keyboard

print(__doc__)
print("-" * 60)
print("En ecoute. Pressez des touches...\n")

pressed = set()


def describe(key):
    char = getattr(key, "char", None)
    vk = getattr(key, "vk", None)
    return f"{key}  (char={char!r}, vk={vk})"


def on_press(key):
    pressed.add(key)
    print(f"  v press   : {describe(key)}")
    combo = " + ".join(sorted(str(k) for k in pressed))
    if len(pressed) > 1:
        print(f"     combo  : {combo}")
    if key == keyboard.Key.esc:
        print("\nEchap detecte : fin du test.")
        return False


def on_release(key):
    pressed.discard(key)


with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
