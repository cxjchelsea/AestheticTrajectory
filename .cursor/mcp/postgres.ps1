$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$envPath = Join-Path $repoRoot "backend\.env"

function Read-DotEnv {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path
    )

    $values = @{}

    if (-not (Test-Path $Path)) {
        return $values
    }

    foreach ($line in Get-Content $Path) {
        $trimmed = $line.Trim()

        if ($trimmed -eq "" -or $trimmed.StartsWith("#")) {
            continue
        }

        $separatorIndex = $trimmed.IndexOf("=")

        if ($separatorIndex -lt 1) {
            continue
        }

        $key = $trimmed.Substring(0, $separatorIndex).Trim()
        $value = $trimmed.Substring($separatorIndex + 1).Trim().Trim('"').Trim("'")
        $values[$key] = $value
    }

    return $values
}

$dotenv = Read-DotEnv -Path $envPath
$databaseUrl = $env:DATABASE_URL

if ([string]::IsNullOrWhiteSpace($databaseUrl)) {
    $databaseUrl = $dotenv["DATABASE_URL"]
}

if ([string]::IsNullOrWhiteSpace($databaseUrl)) {
    $databaseUrl = $dotenv["POSTGRES_DSN"]
}

if ([string]::IsNullOrWhiteSpace($databaseUrl)) {
    $hostName = $dotenv["POSTGRES_HOST"]
    $port = $dotenv["POSTGRES_PORT"]
    $database = $dotenv["POSTGRES_DB"]
    $user = $dotenv["POSTGRES_USER"]
    $password = $dotenv["POSTGRES_PASSWORD"]

    if ([string]::IsNullOrWhiteSpace($hostName)) {
        $hostName = "127.0.0.1"
    }

    if ([string]::IsNullOrWhiteSpace($port)) {
        $port = "5432"
    }

    if ([string]::IsNullOrWhiteSpace($database)) {
        $database = "aesthetic_trajectory"
    }

    if ([string]::IsNullOrWhiteSpace($user)) {
        throw "DATABASE_URL, POSTGRES_DSN, or POSTGRES_USER must be set in backend/.env before starting the PostgreSQL MCP server."
    }

    $encodedUser = [uri]::EscapeDataString($user)
    $encodedPassword = [uri]::EscapeDataString($password)
    $databaseUrl = "postgresql://$encodedUser`:$encodedPassword@$hostName`:$port/$database"
}

# The PostgreSQL MCP package expects a libpq-style URL, not a SQLAlchemy driver URL.
$databaseUrl = $databaseUrl -replace "^postgresql\+[^:]+://", "postgresql://"
$databaseUrl = $databaseUrl -replace "^postgres\+[^:]+://", "postgres://"

$npx = Get-Command npx -ErrorAction Stop
& $npx.Source -y "@modelcontextprotocol/server-postgres" $databaseUrl
exit $LASTEXITCODE
