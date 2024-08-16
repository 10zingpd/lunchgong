{pkgs ? import <nixpkgs> {}}: let
  pkgs = import <nixpkgs> {};
in
  pkgs.mkShell {
    nativeBuildInputs = with pkgs; [
        ngrok
    ];
    shellHook = ''
    '';
  }
