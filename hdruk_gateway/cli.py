#!/usr/bin/env python3
"""
HDR UK Gateway CLI Tool.

A command-line interface for searching and exploring UK health datasets.

Usage:
    python -m hdruk_gateway.cli search "diabetes"
    python -m hdruk_gateway.cli search "cancer data in Wales" --export csv
    python -m hdruk_gateway.cli dataset <dataset_id>
    python -m hdruk_gateway.cli publishers
"""

import argparse
import sys
import json
from typing import Optional

from .client import GatewayClient
from .search import DatasetSearcher
from .models import ResourceType


def format_dataset(dataset, verbose: bool = False) -> str:
    """Format a dataset for display."""
    lines = [
        f"\n{'='*60}",
        f"📊 {dataset.title}",
        f"{'='*60}",
        f"Publisher: {dataset.publisher_name}",
        f"ID: {dataset.id}",
    ]

    if dataset.abstract:
        abstract = dataset.abstract
        if len(abstract) > 300 and not verbose:
            abstract = abstract[:300] + "..."
        lines.append(f"\nAbstract: {abstract}")

    lines.append(f"\nRelated: {dataset.publications_count} publications, {dataset.durs_count} data uses")
    lines.append(f"URL: {dataset.gateway_url}")

    if verbose and dataset.metadata:
        lines.append(f"\nKeywords: {', '.join(dataset.metadata.keywords or [])}")
        if dataset.metadata.spatial:
            lines.append(f"Coverage: {dataset.metadata.spatial}")

    return "\n".join(lines)


def format_data_use(dur, verbose: bool = False) -> str:
    """Format a data use register entry for display."""
    lines = [
        f"\n{'='*60}",
        f"📋 {dur.project_title}",
        f"{'='*60}",
        f"Organisation: {dur.organisation_name or 'Unknown'}",
    ]

    if dur.organisation_sector:
        lines.append(f"Sector: {dur.organisation_sector.value}")

    if dur.lay_summary:
        summary = dur.lay_summary
        if len(summary) > 300 and not verbose:
            summary = summary[:300] + "..."
        lines.append(f"\nSummary: {summary}")

    if dur.latest_approval_date:
        lines.append(f"\nApproved: {dur.latest_approval_date}")

    lines.append(f"URL: {dur.gateway_url}")

    return "\n".join(lines)


def cmd_search(args):
    """Search command handler."""
    searcher = DatasetSearcher()

    print(f"\n🔍 Searching for: {args.query}")
    print("-" * 40)

    result = searcher.search(
        query=args.query,
        include_data_uses=args.include_data_uses,
        include_publications=args.include_publications,
        per_page=args.limit,
    )

    if result.query_interpretation:
        print(f"📝 {result.query_interpretation}")

    print(f"⏱️  Search completed in {result.search_time_ms:.0f}ms")
    print(f"📊 Found {result.total_count} results")

    if args.export:
        if args.export == "csv":
            output = searcher.export_results_csv(result.results)
            filename = f"search_results_{args.query.replace(' ', '_')[:20]}.csv"
        else:
            output = searcher.export_results_json(result.results)
            filename = f"search_results_{args.query.replace(' ', '_')[:20]}.json"

        with open(filename, "w") as f:
            f.write(output)
        print(f"\n✅ Exported to {filename}")
        return

    # Display datasets
    if result.results.datasets:
        print(f"\n\n📊 DATASETS ({len(result.results.datasets)})")
        for ds in result.results.datasets:
            print(format_dataset(ds, verbose=args.verbose))

    # Display data uses
    if result.results.data_uses:
        print(f"\n\n📋 DATA USE REGISTER ({len(result.results.data_uses)})")
        for dur in result.results.data_uses:
            print(format_data_use(dur, verbose=args.verbose))

    # Display publications
    if result.results.publications:
        print(f"\n\n📄 PUBLICATIONS ({len(result.results.publications)})")
        for pub in result.results.publications:
            print(f"\n• {pub.paper_title}")
            if pub.authors:
                print(f"  Authors: {pub.authors}")
            if pub.year_of_publication:
                print(f"  Year: {pub.year_of_publication}")
            print(f"  URL: {pub.gateway_url}")

    # Display facets
    if args.facets and result.facets:
        print("\n\n📊 FACETS")
        for facet in result.facets:
            print(f"\n{facet.name}:")
            for bucket in facet.buckets[:5]:
                print(f"  • {bucket['key']}: {bucket['count']}")

    # Display suggestions
    if result.suggestions:
        print("\n\n💡 SUGGESTIONS")
        for suggestion in result.suggestions[:3]:
            print(f"  • Try: \"{suggestion.text}\"")


def cmd_dataset(args):
    """Get dataset details command handler."""
    client = GatewayClient()

    try:
        dataset = client.get_dataset(args.dataset_id)
        print(format_dataset(dataset, verbose=True))

        if args.similar:
            searcher = DatasetSearcher(client)
            similar = searcher.find_similar_datasets(args.dataset_id)
            if similar:
                print("\n\n🔗 SIMILAR DATASETS")
                for ds in similar:
                    print(f"\n• {ds.title}")
                    print(f"  Publisher: {ds.publisher_name}")
                    print(f"  URL: {ds.gateway_url}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_data_use(args):
    """Get data use details command handler."""
    client = GatewayClient()

    try:
        dur = client.get_data_use(args.dur_id)
        print(format_data_use(dur, verbose=True))

        if dur.public_benefit_statement:
            print(f"\n📌 Public Benefit:\n{dur.public_benefit_statement}")

        if dur.datasets:
            print(f"\n📊 Datasets Used: {', '.join(dur.datasets[:5])}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_publishers(args):
    """List publishers command handler."""
    client = GatewayClient()

    print("\n📋 DATA PUBLISHERS / CUSTODIANS")
    print("=" * 60)

    try:
        publishers = client.list_publishers(per_page=args.limit)

        for pub in publishers:
            print(f"\n• {pub.name}")
            if pub.introduction:
                intro = pub.introduction[:100] + "..." if len(pub.introduction) > 100 else pub.introduction
                print(f"  {intro}")
            if pub.contact_point:
                print(f"  Contact: {pub.contact_point}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_export_dur(args):
    """Export data use register command handler."""
    client = GatewayClient()

    print("\n📥 Exporting Data Use Register...")

    try:
        data_uses = client.export_data_uses()
        print(f"Found {len(data_uses)} data use entries")

        if args.publisher:
            data_uses = [
                dur for dur in data_uses
                if args.publisher.lower() in (dur.organisation_name or "").lower()
            ]
            print(f"Filtered to {len(data_uses)} entries for '{args.publisher}'")

        searcher = DatasetSearcher(client)
        from .models import SearchResult
        result = SearchResult(data_uses=data_uses)

        if args.format == "csv":
            output = searcher.export_results_csv(result)
            filename = f"data_use_register{'_' + args.publisher if args.publisher else ''}.csv"
        else:
            output = searcher.export_results_json(result)
            filename = f"data_use_register{'_' + args.publisher if args.publisher else ''}.json"

        with open(filename, "w") as f:
            f.write(output)

        print(f"✅ Exported to {filename}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_interactive(args):
    """Interactive search mode."""
    searcher = DatasetSearcher()

    print("\n🔬 HDR UK Gateway Interactive Search")
    print("=" * 40)
    print("Type your search query or 'quit' to exit")
    print("Commands: /datasets, /dur, /pubs, /help\n")

    while True:
        try:
            query = input("🔍 Search: ").strip()

            if not query:
                continue

            if query.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break

            if query.startswith("/"):
                cmd = query[1:].lower()
                if cmd == "help":
                    print("\nCommands:")
                    print("  /datasets - Search datasets only")
                    print("  /dur - Search data use register only")
                    print("  /pubs - Search publications only")
                    print("  /help - Show this help")
                    print("  quit - Exit\n")
                    continue

            # Determine what to search
            include_data_uses = "/dur" in query.lower() or not query.startswith("/")
            include_publications = "/pub" in query.lower()

            # Clean command prefixes from query
            clean_query = query
            for prefix in ["/datasets", "/dur", "/pubs"]:
                clean_query = clean_query.replace(prefix, "").strip()

            if not clean_query:
                print("Please enter a search term")
                continue

            result = searcher.search(
                query=clean_query,
                include_data_uses=include_data_uses,
                include_publications=include_publications,
                per_page=5,
            )

            print(f"\n📊 Found {result.total_count} results ({result.search_time_ms:.0f}ms)\n")

            for i, ds in enumerate(result.results.datasets[:5], 1):
                print(f"{i}. 📊 {ds.title[:60]}{'...' if len(ds.title) > 60 else ''}")
                print(f"   Publisher: {ds.publisher_name}")
                print()

            for i, dur in enumerate(result.results.data_uses[:3], 1):
                print(f"{i}. 📋 {dur.project_title[:60]}{'...' if len(dur.project_title) > 60 else ''}")
                print(f"   Org: {dur.organisation_name or 'Unknown'}")
                print()

            if result.suggestions:
                print("💡 Try also:", ", ".join(s.text for s in result.suggestions[:3]))
            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HDR UK Gateway CLI - Search and explore UK health datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "diabetes"
  %(prog)s search "cancer data in Wales" --export csv
  %(prog)s search "cardiovascular" --data-uses --verbose
  %(prog)s dataset <id>
  %(prog)s publishers
  %(prog)s interactive
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for datasets")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("-n", "--limit", type=int, default=10, help="Max results")
    search_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    search_parser.add_argument("--export", choices=["csv", "json"], help="Export format")
    search_parser.add_argument("--data-uses", dest="include_data_uses", action="store_true",
                               default=True, help="Include data use register")
    search_parser.add_argument("--no-data-uses", dest="include_data_uses", action="store_false",
                               help="Exclude data use register")
    search_parser.add_argument("--publications", dest="include_publications", action="store_true",
                               help="Include publications")
    search_parser.add_argument("--facets", action="store_true", help="Show facets")
    search_parser.set_defaults(func=cmd_search)

    # Dataset command
    dataset_parser = subparsers.add_parser("dataset", help="Get dataset details")
    dataset_parser.add_argument("dataset_id", help="Dataset ID")
    dataset_parser.add_argument("--similar", action="store_true", help="Show similar datasets")
    dataset_parser.set_defaults(func=cmd_dataset)

    # Data use command
    dur_parser = subparsers.add_parser("datause", help="Get data use details")
    dur_parser.add_argument("dur_id", help="Data use register ID")
    dur_parser.set_defaults(func=cmd_data_use)

    # Publishers command
    pub_parser = subparsers.add_parser("publishers", help="List data publishers")
    pub_parser.add_argument("-n", "--limit", type=int, default=20, help="Max results")
    pub_parser.set_defaults(func=cmd_publishers)

    # Export DUR command
    export_parser = subparsers.add_parser("export-dur", help="Export data use register")
    export_parser.add_argument("--publisher", help="Filter by publisher")
    export_parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Export format")
    export_parser.set_defaults(func=cmd_export_dur)

    # Interactive command
    int_parser = subparsers.add_parser("interactive", help="Interactive search mode")
    int_parser.set_defaults(func=cmd_interactive)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
