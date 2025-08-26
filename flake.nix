{
  description = "Gingerino's stuff";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
      };
      uv = pkgs.uv;
    in
    {
      packages = rec {
        check = pkgs.writeShellScriptBin "check" ''
          set -eu
          ${uv}/bin/uv run ruff format --check
          ${uv}/bin/uv run ruff check
        '';

        test = pkgs.writeShellScriptBin "test" ''
          set -eu
          ${uv}/bin/uv run pytest
        '';

        build = pkgs.writeShellScriptBin "build" ''
          set -eu
          ${check}/bin/check
          ${test}/bin/test

          rm -rf dist
          ${uv}/bin/uv build "$@"
        '';

        publish = pkgs.writeShellScriptBin "publish" ''
          set -eu
          ${build}/bin/build

          ${uv}/bin/uv publish
        '';
      };
      devShells = {
        default = pkgs.mkShellNoCC {
          buildInputs = [ uv ];
        };
      };
    }
  );
}
