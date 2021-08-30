import vacuna

container = vacuna.Container()


@container.dependency(kind='SINGLETON')
def config(args):
    return {
        'path': args.path,
    }


@container.dependency(kind='SINGLETON')
def args():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        '--beauty',
        default=False,
        action='store_true',
    )
    parser.add_argument('--path', default='.', type=str)

    return parser.parse_args()


class App:
    def __init__(self, path: str, beauty: bool):
        self.path = path
        self.beauty = beauty

    def run(self):
        print(
            'It is alive! '
            f'path: `{self.path}`, '
            f'beauty: `{self.beauty}`.'
        )


@container.dependency(kind='FACTORY')
def app(path: str = config['path'], beauty: bool = args.beauty):
    return App(path, beauty)


@container.dependency()
def main(app: App):
    app.run()


if __name__ == "__main__":
    container.run(main)
