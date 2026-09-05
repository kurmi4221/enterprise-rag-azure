from backend.app.services.azure_ai import project_client

deployments = project_client.deployments.list()

print("=" * 60)
print("Deployments")
print("=" * 60)

for d in deployments:
    print(f"Name : {d.name}")
    print(f"Model: {getattr(d, 'model_name', 'N/A')}")
    print("-" * 60)