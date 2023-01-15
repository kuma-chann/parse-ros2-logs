"""ROS2のログメッセージをパース処理するモジュール

使用例：
    $ python3 parse_ros2_logs.py ./log.txt

    $ python3
    >>> from parse_ros2_logs import ParseRos2Logs
    >>> ros2_logs = ParseRos2Logs()
    >>> txt = '[INFO] [1673415247.564669534] [minimal_publisher]: Publishing: "Hello World: 0"'
    >>> ros2_logs.parse_log(txt)
    >>> print(ros2_logs.get_logs_as_list())
"""


from sys import argv
from os.path import (
    isfile,
    abspath,
)
from pyparsing import (
    Word,
    Suppress,
    alphanums,
    ParseException,
)


class ParseRos2Logs():
    """ROS2のログメッセージを処理するためのクラス

    ログメッセージをリスト型または辞書型に変換する

    Attributes:
        __pattern (ParserElement): ログメッセージのパターン
        __log_data (list[ParseResults]): パース処理したログメッセージ
        __dict_keys (list[str]): パース処理したログメッセージを辞書型で扱う際のキー
    """

    def __init__(self):
        """コンストラクタ

        マッチさせるパターンの定義と必要な変数の定義を行う
        """
        self.__pattern = self.__define_patterns()
        self.__log_data = []
        self.__dict_keys = list(['log_severity', 'timestamp', 'node_name', 'message'])

    def __define_patterns(self):
        """ログメッセージのパターン定義

        ログは [log_severity] [timestamp] [node_name]: message の形を想定している

        Returns:
            ParserElement: ログメッセージのパターン
        """
        header = lambda name: Suppress('[') + Word(alphanums + '!"#$%&\'()*+,-./:;<=>?@\\^_`{|}~').set_results_name(name) + Suppress(']')
        message = Word(alphanums + ' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
        log = header('log_severity') + header('timestamp') + header('node_name') + Suppress(':') + message('message')
        return log

    def parse_log(self, target):
        """ログを1行だけ処理し、その結果を返す

        処理したログメッセージはインスタンスが保持する

        Args:
            target (str): パース処理したいログメッセージ(1行)

        Returns:
            ParseResults: パース処理したログメッセージ(listとdictを含む)
        """
        try:
            result = self.__pattern.parse_string(target)
        except ParseException as e:
            print('Error: The string did not match the pattern.')
            return []
        else:
            self.__log_data.append(result)
            return result

    def parse_logs(self, targets):
        """ログを複数行まとめて処理し、その結果を返す

        処理したログメッセージはインスタンスが保持する

        Args:
            targets (list[str]): パース処理したいログメッセージ(複数行)

        Returns:
            list[ParseResults]: パース処理したログメッセージのリスト(listとdictを含む)
        """
        parse_results = []
        for target in targets:
            try:
                result = self.__pattern.parse_string(target)
            except ParseException as e:
                parse_results.append('')
            else:
                parse_results.append(result)
                self.__log_data.append(result)
        return parse_results

    @property
    def dict_keys(self):
        """ログメッセージを辞書型で扱うためのキー

        ログは [log_severity] [timestamp] [node_name]: message の形を想定している

        Returns:
            list[str]: ログメッセージで利用できる辞書のキー
        """
        return self.__dict_keys

    def get_logs_as_dict(self):
        """ログメッセージを辞書型で受け取る

        Returns:
            list[dict]: 辞書型に変換したパース処理済みのログメッセージ
        """
        tmp = list()
        for log in self.__log_data:
            tmp.append(log.as_dict())
        return tmp

    def get_logs_as_list(self):
        """ログメッセージをリスト型で受け取る

        Returns:
            list[list]: リスト型に変換したパース処理済みのログメッセージ
        """
        tmp = list()
        for log in self.__log_data:
            tmp.append(log.as_list())
        return tmp


def main():
    try:
        if isfile(abspath(argv[1])):
            path = abspath(argv[1])
        else:
            raise ValueError
    except:
        # 引数が無い or 引数がファイルへのパスでない
        print('Usage: parse_ros2_logs.py <log file path>')
        exit(0)

    ros2_logs = ParseRos2Logs()

    with open(path, mode = 'r', encoding = 'utf-8') as f:
        # ファイルからログメッセージを読み込み、パース処理する
        log_data = f.readlines()
        ros2_logs.parse_logs(log_data)

    # 行単位, 半角スペース区切りでパース処理したログメッセージを出力する
    for i in ros2_logs.get_logs_as_list():
        for j in i:
            print('{} '.format(j), end = '')
        print('')


if __name__ == '__main__':
    main()