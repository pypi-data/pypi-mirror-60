from ..config.config import Config
from ..mt.article import Article
from ..markdown.writer import Writer


class Converter:
    def convert(self, config):
        writer = Writer(config)
        input_path = config.get_input_file_path()
        with open(input_path, "r") as fp:
            article = Article(config)
            for line in fp:
                if article.will_end(line):
                    if not article.fullfilled():
                        print("WARN: the article has not enough attributes.")
                    writer.write(article)
                article = article.append_line(line)
