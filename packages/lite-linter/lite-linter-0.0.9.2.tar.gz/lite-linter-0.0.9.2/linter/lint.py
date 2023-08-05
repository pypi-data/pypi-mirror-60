import sys

from linter.linters import headings
from linter.linters.base import LintController


def main():
    LintController(
        linters=[
            headings.CheckHeadings,
            headings.TagsSpacing,
            headings.UnusedFiles,
            headings.PreventInlineStyles,
            headings.OneLoadBlock,
            headings.EnsureAllIDsAreUnique,
            headings.BlockOrdering,
            headings.BlocksSpacing,
            headings.PreventTwoPaneOverwite,
            headings.CheckFilenames,
            # headings.AllTagsUsed,
            # headings.EnforceBlockTitle,
            # headings.FindHardcodedStrings,
            # headings.EnforceSingleQuotesInBlocks,
            # headings.TabsOverSpaces,
        ]
    ).output()


if __name__ == "__main__":
    sys.exit(main())
