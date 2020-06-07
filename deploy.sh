gcloud beta compute scp --zone "europe-west6-a" --project "tfg-tests-278517" clone_and_build.sh "tfg-tests":~
gcloud beta compute ssh --zone "europe-west6-a" "tfg-tests" --project "tfg-tests-278517" --command "source clone_and_build.sh"

