#!/usr/bin/env python3
import json, click
from pathlib import Path
from rich.console import Console
from .health import check_tcp, check_http, aggregate
console = Console()
@click.group()
@click.version_option()
def main(): pass
@main.command()
@click.option('--config', required=True, help='JSON file: [{"kind":"tcp","host":"127.0.0.1","port":6379},{"kind":"http","url":"http://127.0.0.1:8080/health"}]')
@click.option('--output', '-o', default='results/health.json')
def check(config, output):
    spec = json.loads(Path(config).read_text())
    checks = []
    for item in spec:
        if item['kind'] == 'tcp':
            checks.append(check_tcp(item['host'], item['port'], item.get('timeout', 1.0)))
        else:
            checks.append(check_http(item['url'], item.get('timeout', 3.0)))
    result = aggregate(checks)
    console.print(f"[bold]status: {result['status']}[/bold]")
    for d in result['dependencies']:
        mark = '[green]ok[/green]' if d['ok'] else f"[red]fail[/red] ({d['error']})"
        console.print(f"  {d['target']}: {mark} {d['ms']}ms")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(result, indent=2))
    console.print(f'[green]saved {output}[/green]')
if __name__ == '__main__': main()
