# -*- coding: utf-8 -*-

from pygments.style import Style
from pygments.token import *


class PSCodeStyleDark(Style):
    """
    This style mimics the Monokai color scheme.
    """

    name = "PSDark"
    background_color = '#252525'
    highlight_color = '#353535'

    styles = {
        # No corresponding class for the following:
        Text:                      "#fdfdfd",  # class:  ''
        Whitespace:                "",        # class: 'w'
        Error:                     "#960050 bg:#1e0010",  # class: 'err'
        Other:                     "",        # class 'x'

        Comment:                   "#42a199",  # class: 'c'
        Comment.Multiline:         "",        # class: 'cm'
        Comment.Preproc:           "",        # class: 'cp'
        Comment.Single:            "",        # class: 'c1'
        Comment.Special:           "",        # class: 'cs'

        Keyword:                   "#66d9ef",  # class: 'k'
        Keyword.Constant:          "",        # class: 'kc'
        Keyword.Declaration:       "",        # class: 'kd'
        Keyword.Namespace:         "#f92672",  # class: 'kn'
        Keyword.Pseudo:            "",        # class: 'kp'
        Keyword.Reserved:          "",        # class: 'kr'
        Keyword.Type:              "",        # class: 'kt'

        Operator:                  "#f92672",  # class: 'o'
        Operator.Word:             "",        # class: 'ow' - like keywords

        Punctuation:               "#f8f8f2",  # class: 'p'

        Name:                      "#f8f8f2",  # class: 'n'
        Name.Attribute:            "#a6e22e",  # class: 'na' - to be revised
        Name.Builtin:              "#66d9ef",  # class: 'nb'
        Name.Builtin.Pseudo:       "",        # class: 'bp'
        Name.Class:                "#a6e22e",  # class: 'nc' - to be revised
        Name.Constant:             "#66d9ef",  # class: 'no' - to be revised
        Name.Decorator:            "#a6e22e",  # class: 'nd' - to be revised
        Name.Entity:               "",        # class: 'ni'
        Name.Exception:            "#a6e22e",  # class: 'ne'
        Name.Function:             "#a6e22e",  # class: 'nf'
        Name.Property:             "",        # class: 'py'
        Name.Label:                "",        # class: 'nl'
        Name.Namespace:            "",        # class: 'nn' - to be revised
        Name.Other:                "#a6e22e",  # class: 'nx'
        Name.Tag:                  "#f92672",  # class: 'nt' - like a keyword
        Name.Variable:             "",        # class: 'nv' - to be revised
        Name.Variable.Class:       "",        # class: 'vc' - to be revised
        Name.Variable.Global:      "",        # class: 'vg' - to be revised
        Name.Variable.Instance:    "",        # class: 'vi' - to be revised

        Number:                    "#ae81ff",  # class: 'm'
        Number.Float:              "",        # class: 'mf'
        Number.Hex:                "",        # class: 'mh'
        Number.Integer:            "",        # class: 'mi'
        Number.Integer.Long:       "",        # class: 'il'
        Number.Oct:                "",        # class: 'mo'

        Literal:                   "#ae81ff",  # class: 'l'
        Literal.Date:              "#e6db74",  # class: 'ld'

        String:                    "#e6db74",  # class: 's'
        String.Backtick:           "",        # class: 'sb'
        String.Char:               "",        # class: 'sc'
        String.Doc:                "",        # class: 'sd' - like a comment
        String.Double:             "",        # class: 's2'
        String.Escape:             "#ae81ff",  # class: 'se'
        String.Heredoc:            "",        # class: 'sh'
        String.Interpol:           "",        # class: 'si'
        String.Other:              "",        # class: 'sx'
        String.Regex:              "",        # class: 'sr'
        String.Single:             "",        # class: 's1'
        String.Symbol:             "",        # class: 'ss'

        Generic:                   "",        # class: 'g'
        Generic.Deleted:           "#f92672",  # class: 'gd',
        Generic.Emph:              "italic",  # class: 'ge'
        Generic.Error:             "",        # class: 'gr'
        Generic.Heading:           "",        # class: 'gh'
        Generic.Inserted:          "#a6e22e",  # class: 'gi'
        Generic.Output:            "",        # class: 'go'
        Generic.Prompt:            "",        # class: 'gp'
        Generic.Strong:            "bold",    # class: 'gs'
        Generic.Subheading:        "#75715e",  # class: 'gu'
        Generic.Traceback:         "",        # class: 'gt'
    }


class PSCodeStyleLight(Style):
    """
    This style mimics the Monokai color scheme.
    """

    name = "PSLight"
    background_color = '#fefefe'
    highlight_color = '#dcdcdc'

    styles = {
        # No corresponding class for the following:
        Text:                      "#000000",  # class:  ''
        Whitespace:                "",        # class: 'w'
        Error:                     "#960050 bg:#1e0010",  # class: 'err'
        Other:                     "",        # class 'x'

        Comment:                   "#75715e",  # class: 'c'
        Comment.Multiline:         "",        # class: 'cm'
        Comment.Preproc:           "",        # class: 'cp'
        Comment.Single:            "",        # class: 'c1'
        Comment.Special:           "",        # class: 'cs'

        Keyword:                   "#66d9ef",  # class: 'k'
        Keyword.Constant:          "",        # class: 'kc'
        Keyword.Declaration:       "",        # class: 'kd'
        Keyword.Namespace:         "#f92672",  # class: 'kn'
        Keyword.Pseudo:            "",        # class: 'kp'
        Keyword.Reserved:          "",        # class: 'kr'
        Keyword.Type:              "",        # class: 'kt'

        Operator:                  "#f92672",  # class: 'o'
        Operator.Word:             "",        # class: 'ow' - like keywords

        Punctuation:               "#f8f8f2",  # class: 'p'

        Name:                      "#f8f8f2",  # class: 'n'
        Name.Attribute:            "#a6e22e",  # class: 'na' - to be revised
        Name.Builtin:              "",        # class: 'nb'
        Name.Builtin.Pseudo:       "",        # class: 'bp'
        Name.Class:                "#a6e22e",  # class: 'nc' - to be revised
        Name.Constant:             "#66d9ef",  # class: 'no' - to be revised
        Name.Decorator:            "#a6e22e",  # class: 'nd' - to be revised
        Name.Entity:               "",        # class: 'ni'
        Name.Exception:            "#064224",  # class: 'ne'
        Name.Function:             "#064224",  # class: 'nf'
        Name.Property:             "",        # class: 'py'
        Name.Label:                "",        # class: 'nl'
        Name.Namespace:            "",        # class: 'nn' - to be revised
        Name.Other:                "#a6e22e",  # class: 'nx'
        Name.Tag:                  "#f92672",  # class: 'nt' - like a keyword
        Name.Variable:             "",        # class: 'nv' - to be revised
        Name.Variable.Class:       "",        # class: 'vc' - to be revised
        Name.Variable.Global:      "",        # class: 'vg' - to be revised
        Name.Variable.Instance:    "",        # class: 'vi' - to be revised

        Number:                    "#ae81ff",  # class: 'm'
        Number.Float:              "",        # class: 'mf'
        Number.Hex:                "",        # class: 'mh'
        Number.Integer:            "",        # class: 'mi'
        Number.Integer.Long:       "",        # class: 'il'
        Number.Oct:                "",        # class: 'mo'

        Literal:                   "#ae81ff",  # class: 'l'
        Literal.Date:              "#e6db74",  # class: 'ld'

        String:                    "#d2691e",  # class: 's'
        String.Backtick:           "",        # class: 'sb'
        String.Char:               "",        # class: 'sc'
        String.Doc:                "",        # class: 'sd' - like a comment
        String.Double:             "",        # class: 's2'
        String.Escape:             "#ae81ff",  # class: 'se'
        String.Heredoc:            "",        # class: 'sh'
        String.Interpol:           "",        # class: 'si'
        String.Other:              "",        # class: 'sx'
        String.Regex:              "",        # class: 'sr'
        String.Single:             "",        # class: 's1'
        String.Symbol:             "",        # class: 'ss'

        Generic:                   "",        # class: 'g'
        Generic.Deleted:           "#f92672",  # class: 'gd',
        Generic.Emph:              "italic",  # class: 'ge'
        Generic.Error:             "",        # class: 'gr'
        Generic.Heading:           "",        # class: 'gh'
        Generic.Inserted:          "#a6e22e",  # class: 'gi'
        Generic.Output:            "",        # class: 'go'
        Generic.Prompt:            "",        # class: 'gp'
        Generic.Strong:            "bold",    # class: 'gs'
        Generic.Subheading:        "#75715e",  # class: 'gu'
        Generic.Traceback:         "",        # class: 'gt'
    }
