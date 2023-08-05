# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tests', 'tproj', 'tproj.utils']

package_data = \
{'': ['*']}

install_requires = \
['pyyaml>=5.3,<6.0']

entry_points = \
{'console_scripts': ['tproj = tproj.cli:main']}

setup_kwargs = {
    'name': 'tproj-zombie110year',
    'version': '1.0.3',
    'description': 'tproj 用于管理用户创建的项目模板，一个项目所需的起始文件、目录被包含在一个 zip 格式的压缩包中。',
    'long_description': '# tproj\n\ntproj 用于管理用户创建的项目模板，一个项目所需的起始文件、目录被包含在一个 zip 格式的压缩包中。\n\n## install\n\n- 通过源码安装\n\n```sh\ngit clone https://github.com/zombie110year/tproj-py.git\ncd tproj-py && python setup.py install\n```\n\n- 通过 pip 安装\n\n```sh\npip install tproj-zombie110year\n```\n\n- 通过 pipx 安装\n\n更推荐使用此方法， pipx 是一个用于安装基于 Python 的应用程序的包管理器，相比 pip\n它会创建独立的虚拟环境，不会污染当前 Python 环境。\n\n```sh\npipx install tproj-zombie110year\n```\n\n## usage\n\ntproj 提供名为 tproj 的可执行文件，可以：根据当前目录内容创建归档并自动重命名、\n移动至数据目录中，应用模板归档创建项目，浏览已有的归档。\n\n### 创建模板归档\n\n创建归档使用 `tproj create` 子命令，默认将当前目录下的所有文件以及子目录中的文件递归地添加到归档中。\n并且通过 stdin 询问归档名称，最终保存到 `$TPROJ_HOME/template` 目录下。\n\n除此之外还提供以下参数：\n\n- `-n/--name` 直接在命令行参数中指定归档名（将会覆盖 tproj.cfg 中的设置）\n- `-f/--force` 覆盖同名归档（默认取消创建）\n\n<!-- TODO\n- `--git-archive` 调用 git archive 子命令来创建归档，在这个参数之后的参数会传递给 git archive 命令\n- `--exclude` 忽略列表，遵守 gitignore 类似的语法，每个实体之间用 `:` 冒号分隔\n- `--ignorefile` 与 `--exclude` 作用相同，但从文件中读取规则，文件采用和 gitignore 相同的语法\n  - 如果 `--ignorefile` 与 `--exclude` 同时使用，最后的应用的规则会取并集\n-->\n\n这要求在项目的根目录下存在一个名为 `tproj.cfg` 的文件，在这个文件中定义此模板的相关参数。\n可配置的各键值对参考 [tproj.cfg](#tproj.cfg).\n\n示例\n\n```sh\ntproj create -n helloworld\n```\n\n### 应用模板归档\n\n应用指定的归档，使用 `tproj apply` 子命令，扫描 `$TPROJ_HOME/template` 目录下的模板归档，将其解压至当前工作目录。\n\n具有特性\n\n- 不输入 .zip 后缀，程序会自动添加，如果输入了 .zip 后缀，那么 tproj 将会寻找名称类似于 \\*.zip.zip 的归档\n- 不需要输入完整的模板名，只要输入足够唯一确定一个模板的名字即可，但如果输入对应了多个模板，程序将终止\n\n除此之外还提供以下参数：\n\n- `-O/--out-dir` 解压至指定目录，而非当前工作目录（不存在会创建）\n\n示例\n\n```sh\nmkdir helloworld\ncd helloworld\ntproj apply helloworld\n```\n\n### 浏览已有模板\n\n浏览已有模板，使用 `tproj ls` 子命令，将列出 `$TRPOJ_HOME/template` 下的归档文件（去除 .zip 后缀）\n\n示例\n\n```sh\ntproj ls\n```\n\n## 参考资料\n\n### 文件系统\n\ntproj 的所有数据文件都保存在特定的目录中，将这个目录所在的路径称为 `TPROJ_HOME`，\n可以修改环境变量 `TPROJ_HOME` 来修改此目录的路径，如果未设置此环境变量，那么将使用以下默认值：\n\n- 对于 Windows 系统，默认使用 `%APPDATA%\\tproj`\n- 对于 Linux 系统，遵守 XDG 规范，默认使用 `$XDG_DATA_HOME/tproj`\n\n  - 有些 Linux 没有提供 `$XDG_*` 变量，那么就直接使用 `~/.local/share/tproj`\n\n- 归档文件存储在 `$TPROJ_HOME/template` 目录下\n- 配置文件存储为文件 `$TPROJ_HOME/tproj.conf`（TOOD）\n\n### tproj 包\n\n一个 tproj 包实质上是一个用过 Deflate 算法压缩的归档文件，并且以 `.zip` 为后缀名。\n除了用 `tproj create -n ...` 来创建之外，也可以使用你喜欢的任何压缩工具来打包。\n项目所需的文件原样存储在归档的 "根目录" 中，并在应用时原样解压到当前工作目录或\n`tproj apply -d ...` 指定的目录中。\n\n### tproj.yml\n\n|     键      |   类型    |     默认值      | 含义                       |\n| :---------: | :-------: | :-------------: | -------------------------- |\n|    name     |    str    |      `""`       | 此模板的名字               |\n|   author    |    str    |      `""`       | 模板的作者，`name<email>`  |\n|   include   | List[str] |   `["**/*"]`    | 默认包含所有文件、子目录   |\n|   exclude   | List[str] | `[".git/**/*"]` | 被排除的文件               |\n| description |    str    |                 | （可选）一段对该模板的描述 |\n\n示例\n\n```yaml\nname: "helloworld"\nauthor: "zombie110year<zombie110year@outlook.com>"\ninclude:\n  - "README.md"\n  - ".gitignore"\n  - "src/**"\n  - "tests/**"\n```\n',
    'author': 'zombie110year',
    'author_email': 'zombie110year@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zombie110year/tproj-py/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
