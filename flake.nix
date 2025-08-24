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
          ${uv}/bin/uv run ruff format --check
          ${uv}/bin/uv run ruff check
        '';

        test = pkgs.writeShellScriptBin "test" ''
          ${uv}/bin/uv run pytest
        '';

        build = pkgs.writeShellScriptBin "build" ''
          ${check}/bin/check
          ${test}/bin/test

          rm -rf dist
          ${uv}/bin/uv build "$@"
        '';

        publish = pkgs.writeShellScriptBin "publish" ''
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
