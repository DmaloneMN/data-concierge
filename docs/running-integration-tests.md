# Running Integration Tests

Integration tests require a live Microsoft Fabric SQL Analytics Endpoint.
They are **automatically skipped** in CI unless `FABRIC_SQL_ENDPOINT` is set,
so running `pytest tests/unit/` is always safe without Fabric credentials.

---

## Prerequisites

### 1. Install ODBC Driver 18 for SQL Server

**Windows:**
[Download from Microsoft](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

**Linux (Ubuntu/Debian):**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

**macOS (Homebrew):**
```bash
brew install msodbcsql18
```

### 2. Install `pyodbc`
```bash
pip install pyodbc
```

### 3. Configure your `.env`
```dotenv
FABRIC_SQL_ENDPOINT=<your-fabric-sql-endpoint>
FABRIC_DATABASE=<your-database-name>
```

---

## Running the Tests

```bash
pytest tests/integration/ -v
```
