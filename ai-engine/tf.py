import subprocess

def run_terraform():
    try:
        # Initialize Terraform
        subprocess.run(
            ["terraform", "init"],
            cwd="../terraform",
            text=True,
            check=True
        )
        print("Terraform Init Completed\n")

        # Plan Terraform configuration
        subprocess.run(
            ["terraform", "plan", "-out=tfplan"],
            cwd="../terraform",
            text=True,
            check=True,
        )
        print("Terraform Plan Completed\n")

        # Save plan output as JSON
        with open("../ai-engine/plan.json", "w") as f:
            subprocess.run(
                ["terraform", "show", "-json", "tfplan"],
                cwd="../terraform",
                stdout=f,  
                text=True,
                check=True,
            )

        print("Terraform Plan Output Saved to JSON\n")

    except subprocess.CalledProcessError as e:
        print("Error running terraform:\n", e.stderr)
        return None

run_terraform()