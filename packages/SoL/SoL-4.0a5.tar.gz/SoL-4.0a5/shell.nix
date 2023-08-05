# -*- coding: utf-8 -*-
# :Project:   SoL -- nix environment
# :Created:   sab 04 ago 2018 22:57:25 CEST
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Alberto Berti
#

let
  inherit (import <nixpkgs> {}) mkShell;
  sol = import ./release.nix {};
in
  mkShell {
    inputsFrom = [ sol ];
    shellHook = "";
}
