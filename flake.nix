{
  description = "Dev shell for AREMA ontology test run";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            curl
            jq
            uv
            python311
            minikube
            kubectl
          ];

          shellHook = ''
            echo "AREMA ontology dev shell"
            echo ""
            echo "Docker Compose (quick dev loop):"
            echo "  docker compose up --build"
            echo "  curl -X PUT http://localhost:8000/update"
            echo "  curl http://localhost:8000/"
            echo ""
            echo "Kubernetes (test k8s manifests):"
            echo "  minikube start --driver=docker"
            echo "  docker build -t arema-ontology:latest . && minikube image load arema-ontology:latest"
            echo "  kubectl apply -f k8s/"
            echo "  kubectl port-forward deploy/fuseki 3030:3030"
            echo "  kubectl port-forward deploy/arema-ontology 8000:8000"
            echo ""
            if [ -f .env ]; then
              export $(grep -v '^#' .env | xargs)
              echo ".env loaded"
            fi
          '';
        };
      });
}
