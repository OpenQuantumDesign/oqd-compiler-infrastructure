{
  description = "OpenQuantum Design Compiler Infrastructure";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python311;
        pythonPackages = python.pkgs;
      in
      {
        packages.default = pythonPackages.callPackage ./pkgs/derivation.nix { };

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            # Python with dependencies
            (python.withPackages (ps: with ps; [
              # Core dependencies
              pydantic

              # Documentation dependencies
              pymdown-extensions
              mkdocstrings
              mkdocs-material
              mkdocstrings-python

              # Test dependencies
              pytest

              # Development tools
              pip
              black
              isort
              mypy
            ]))

            # Additional development tools
            git
          ];

          shellHook = ''
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            echo "OpenQuantum Design Compiler Infrastructure development environment"
            echo "Python version: $(python --version)"
          '';
        };
      }
    );
}
