{
  description = "Gingerino's stuff";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
      };

      p2nix = poetry2nix.lib.mkPoetry2Nix {
        inherit pkgs;
      };

      gingerino = p2nix.mkPoetryApplication {
        projectDir = self;
        python = pkgs.python313;
        preferWheels = true;
        checkPhase = ''
          runHook preCheck

          ruff check .
          ruff format --check .
          pytest

          runHook postCheck
        '';
      };
    in
    {
      packages = {
        default = gingerino;
      };
      devShells = {
        default = pkgs.mkShellNoCC {
          buildInputs = gingerino.buildInputs;
        };
      };
    }
  );
}
