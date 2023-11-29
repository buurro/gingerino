{
  description = "Gingerino's stuff";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryEnv mkPoetryApplication;
      gingerino = mkPoetryApplication {
        projectDir = self;
        python = pkgs.python311;
        preferWheels = true;
        checkPhase = ''
          runHook preCheck

          python -m pytest

          runHook postCheck
        '';
      };
    in
    {
      packages.default = gingerino;
    }
  );
}
