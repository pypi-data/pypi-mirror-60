from linters import headings
from linters.base import LintController

if __name__ == "__main__":
    LintController(
        linters=[
            headings.CheckHeadings,
            headings.TagsSpacing,
            headings.UnusedFiles,
            headings.PreventInlineStyles,
            headings.OneLoadBlock,
            headings.AllTagsUsed,
            headings.EnsureAllIDsAreUnique,
            headings.BlockOrdering,
            headings.BlocksSpacing,
            headings.PreventTwoPaneOverwite,
            headings.CheckFilenames,
            headings.EnforceBlockTitle,
            headings.FindHardcodedStrings,
            headings.EnforceSingleQuotesInBlocks,
            headings.TabsOverSpaces,
        ]
    ).output()
