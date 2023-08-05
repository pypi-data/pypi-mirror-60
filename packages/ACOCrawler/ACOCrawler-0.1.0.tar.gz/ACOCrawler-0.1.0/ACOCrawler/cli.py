import click

from .acocrawler import AcoCrawler


def solver_options(f):
    click.option('--keyword', type=str, default='competitive programming')(f)
    click.option('--keywords', multiple=True, default=['c++', 'atcoder', 'codeforces'])(f)
    click.option('--num_of_cycles', type=int, default=100)(f)
    click.option('--num_of_ants', type=int, default=10)(f)
    click.option('--alpha', type=float, default=1)(f)
    click.option('--beta', type=float, default=1)(f)
    click.option('--rho', type=float, default=0.9)(f)
    click.option('--lower', type=float, default=0.01)(f)
    click.option('--upper', type=float, default=10)(f)
    click.option('--base_phe', type=float, default=100)(f)
    click.option('--init_phe', type=float, default=0.1)(f)
    click.option('--collect_norm', type=float, default=0.000001)(f)
    click.option('--init_node_score', type=float, default=0.1)(f)
    return f


@click.group()
def main():
    pass


@main.command(short_help='aco crawler')
@solver_options
def crawl(keyword, keywords, num_of_cycles, num_of_ants, alpha, beta, rho, lower, upper, base_phe, init_phe, collect_norm, init_node_score):
    try:
        keywords = list(keywords)
        crawler = AcoCrawler(keyword, num_of_cycles, num_of_ants, keywords, alpha, beta, rho, lower, upper, base_phe, init_phe, collect_norm, init_node_score)
    except Exception:
        raise click.UsageError("sorry options error")
    crawler.start()
    crawler.solve()
    crawler.finish()


if __name__ == '__main__':
    main()
