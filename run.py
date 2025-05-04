import os

# Define the folder and file structure
structure = {
    "frontend": {
        ".": [
            "index.html", "login.html", "register.html",
            "style.css", "auth.js"
        ],
        "assets": {
            "images": [],
            "js": [],
            "css": []
        },
        "common": ["navbar.js", "utils.js", "api.js"],
        "supply_chain_manager": [
            "dashboard.html", "demand_forecast.html", "inventory.html",
            "sales.html", "logs.html"
        ],
        "warehouse": ["dashboard.html", "optimize.html"],
        "procurement": ["dashboard.html", "suppliers.html"],
        "supplier": ["dashboard.html", "order.html"],
        "sales_officer": ["dashboard.html"]
    }
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        os.makedirs(path, exist_ok=True)
        if isinstance(content, dict):
            create_structure(path, content)
        elif isinstance(content, list):
            for file in content:
                if file == ".":
                    continue
                file_path = os.path.join(path, file)
                with open(file_path, "w") as f:
                    f.write(f"// {file} placeholder\n")

# Create the structure in current directory
create_structure(".", structure)

print("Frontend folder structure created successfully.")
