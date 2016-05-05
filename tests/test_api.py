# =============================================================================
# eveapi module demonstration script - Jamie van den Berge
# =============================================================================
#
# This file is in the Public Domain - Do with it as you please.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE
#
# ----------------------------------------------------------------------------

import mock
import pytest
from datetime import datetime

import eveapi


def test_alliance_list(api):
    """EXAMPLE 1: GETTING THE ALLIANCE LIST
    (and showing alliances with 1000 or more members)
    """

    # Let's get the list of alliances.
    # The API function we need to get the list is:
    #
    #    /eve/AllianceList.xml.aspx
    #
    # There is a 1:1 correspondence between folders/files and attributes on api
    # objects, so to call this particular function, we simply do this:
    result1 = api.eve.AllianceList()

    # This result contains a rowset object called "alliances". Rowsets are like
    # database tables and you can do various useful things with them. For now
    # we'll just iterate over it and display all alliances with more than 1000
    # members:

    assert result1.alliances, "no alliance results found"

    for alliance in result1.alliances:
        if alliance.memberCount >= 1000:
            print("{} <{}> has {:,d} members".format(
                alliance.name,
                alliance.shortName,
                alliance.memberCount,
            ))

    return result1.alliances


def test_wallet_balance(authenticated_api):
    """EXAMPLE 2: GETTING WALLET BALANCE OF ALL YOUR CHARACTERS"""

    # To get any info on character/corporation related stuff, we need to
    # acquire an authentication context. All API requests that require
    # authentication need to be called through this object. While it is
    # possible to call such API functions directly through the api object,
    # you would have to specify the userID and apiKey on every call. If you
    # are iterating over many accounts, that may actually be the better
    # option. However, for these examples we only  use one account, so this
    # is more convenient.

    # Now let's say you want to the wallet balance of all your characters.
    # The API function we need to get the characters on your account is:
    #
    #    /account/Characters.xml.aspx
    #
    # As in example 1, this simply means adding folder names as attributes
    # and calling the function named after the base page name:
    result2 = authenticated_api.account.Characters()

    # Some tracking for later examples.
    rich = 0
    rich_charID = 0

    # Now the best way to iterate over the characters on your account and show
    # the isk balance is probably this way:
    for character in result2.characters:
        wallet = authenticated_api.char.AccountBalance(
            characterID=character.characterID
        )
        isk = wallet.accounts[0].balance
        assert isinstance(isk, float)
        print("{} has {:,.2f} ISK.".format(character.name, isk))

        if isk > rich:
            rich = isk
            rich_charID = character.characterID

    return rich_charID


def test_failures(api):
    """EXAMPLE 3: WHEN STUFF GOES WRONG"""
    # Obviously you cannot assume an API call to succeed. There's a myriad of
    # things that can go wrong:
    #
    # - Connection error
    # - Server error
    # - Invalid parameters passed
    # - Hamsters died
    #
    # Therefor it is important to handle errors properly. eveapi will raise
    # an AttributeError if the requested function does not exist on the server
    # (ie. when it returns a 404), a RuntimeError on any other webserver error
    # (such as 500 Internal Server error).
    # On top of this, you can get any of the httplib (which eveapi uses) and
    # socket (which httplib uses) exceptions so you might want to catch those
    # as well.
    #

    with pytest.raises(eveapi.Error) as error:
        # Try calling account/Characters without authentication context
        api.account.Characters()

    assert error.value.code == 400
    assert error.value.args[0] == (
        "'/account/Characters.xml.aspx' request failed (Bad Request)"
    )


# -----------------------------------------------------------------------------
def test_character_sheet(authenticated_api):
    """EXAMPLE 4: GETTING CHARACTER SHEET INFORMATION"""

    # We grab ourselves a character context object.
    # Note that this is a convenience function that takes care of passing the
    # characterID=x parameter to every API call much like auth() does (in fact
    # it's exactly like that, apart from the fact it also automatically adds
    # the "/char" folder). Again, it is possible to use the API functions
    # directly from the api or auth context, but then you have to provide the
    # missing keywords on every call (characterID in this case).
    #
    # The victim we'll use is the last character on the account we used in
    # example 2.
    rich_charID = test_wallet_balance(authenticated_api)
    me = authenticated_api.character(rich_charID)

    # Now that we have a character context, we can display skills trained on
    # a character. First we have to get the skill tree. A real application
    # would cache this data; all objects returned by the api interface can be
    # pickled.
    skilltree = authenticated_api.eve.SkillTree()

    # Now we have to fetch the charactersheet.
    # Note that the call below is identical to:
    #
    #   acc.char.CharacterSheet(characterID=your_character_id)
    #
    # But, as explained above, the context ("me") we created automatically
    # takes care of adding the characterID parameter and /char folder attribute
    sheet = me.CharacterSheet()

    # This list should look familiar. They're the skillpoints at each level for
    # a rank 1 skill. We could use the formula, but this is much simpler :)
    sp = [0, 250, 1414, 8000, 45255, 256000]

    total_sp = 0
    total_skills = 0

    # Now the fun bit starts. We walk the skill tree, and for every group in
    # the tree...
    for g in skilltree.skillGroups:

        skills_trained_in_this_group = False

        # ... iterate over the skills in this group...
        for skill in g.skills:

            # see if we trained this skill by checking the character sheet
            trained = sheet.skills.Get(skill.typeID, False)
            if trained:
                # yep, we trained this skill.

                # print the group name if we haven't done so already
                if not skills_trained_in_this_group:
                    print(g.groupName)
                    skills_trained_in_this_group = True

                # and display some info about the skill!
                print("- {} Rank({}) - SP: {:,d}/{:,d} - Level: {}".format(
                    skill.typeName, skill.rank, trained.skillpoints,
                    (skill.rank * sp[trained.level]), trained.level)
                )
                total_skills += 1
                total_sp += trained.skillpoints

    # And to top it off, display totals.
    print("You currently have {} skills and {:,d} skill points".format(
        total_skills, total_sp)
    )


def test_rowsets(api):
    """EXAMPLE 5: USING ROWSETS"""

    # For this one we will use the result1 that contains the alliance list from
    # the first example.
    rowset = test_alliance_list(api)

    # Now, what if we want to sort the alliances by ticker name. We could
    # unpack all alliances into a list and then use python's sort(key=...) on
    # that list, but that's not efficient. The rowset objects support sorting
    # on columns directly:
    rowset.SortBy("shortName")

    # Note the use of Select() here. The Select method speeds up iterating over
    # large rowsets considerably as no temporary row instances are created.
    for ticker in rowset.Select("shortName"):
        assert ticker

    # The sort above modified the result inplace. There is another method,
    # called SortedBy, which returns a new rowset.
    sorted_by = rowset.SortedBy("allianceID", reverse=True)
    assert id(sorted_by) != id(rowset)

    # Another useful method of rowsets is IndexBy, which enables you to do
    # direct key lookups on columns. We already used this feature in example 3.
    # Indeed most rowsets returned are IndexRowsets already if the data has a
    # primary key attribute defined in the <rowset> tag in the XML data.
    #
    # IndexRowsets are efficient, they reference the data from the rowset they
    # were created from, and create an index mapping on top of it.
    #
    # Anyway, to create an index:
    alliances_by_ticker = rowset.IndexedBy("shortName")

    # Now use the Get() method to get a row directly.
    # Assumes ISD alliance exists. If it doesn't, we probably have bigger
    # problems than the unhandled exception here -_-
    assert alliances_by_ticker.Get("ISD")

    # You may specify a default to return in case the row wasn't found:
    assert alliances_by_ticker.Get("123456", 42) == 42

    # If no default was specified and you try to look up a key that does not
    # exist, an appropriate exception will be raised:
    with pytest.raises(KeyError):
        alliances_by_ticker.Get("123456")


def test_file_caching_data(file_cache):
    """EXAMPLE 6: CACHING DATA"""

    # Now try out the handler! Even though were initializing a new api object
    # here, a handler can be attached or removed from an existing one at any
    # time with its setcachehandler() method.
    cached_api = eveapi.EVEAPIConnection(cacheHandler=file_cache)

    assert len(cached_api._root._handler.cache) == 0

    cached_api.eve.SkillTree()
    assert len(cached_api._root._handler.cache) == 1

    # the second time it should be returning the cached version
    with mock.patch.object(eveapi.context, "httplib") as patched_httplib:
        cached_api.eve.SkillTree()

    assert len(cached_api._root._handler.cache) == 1
    assert patched_httplib.called is False


def test_transactions(file_cache, key_id, vcode):
    """EXAMPLE 7: TRANSACTION DATA
    (and doing more nifty stuff with rowsets)"""

    file_cached_auth_api = eveapi.EVEAPIConnection(
        cacheHandler=file_cache
    ).auth(keyID=key_id, vCode=vcode)

    rich_char_id = test_wallet_balance(file_cached_auth_api)
    rich_char = file_cached_auth_api.character(rich_char_id)
    journal = rich_char.WalletJournal()

    # Let's see how much we paid SCC in transaction tax in the first page
    # of data!

    # Righto, now we -could- sift through the rows and extract what we want,
    # but we can do it in a much more clever way using the GroupedBy method
    # of the rowset in the result. This creates a mapping that maps keys
    # to Rowsets of all rows with that key value in specified column.
    # These data structures are also quite efficient as the only extra data
    # created is the index and grouping.
    entriesByRefType = journal.transactions.GroupedBy("refTypeID")

    # Also note that we're using a hardcoded refTypeID of 54 here. You're
    # supposed to use .eve.RefTypes() though (however they are not likely
    # to be changed anyway so we can get away with it)
    # Note the use of Select() to speed things up here.
    amount = 0.0
    date = 0
    try:
        for result in entriesByRefType[54].Select("amount", "date"):
            tax_amount, date = result
            assert isinstance(date, datetime)
            amount -= tax_amount
    except KeyError:  # no taxes paid
        pass

    print("You paid a {:,.2f} ISK transaction tax since {}".format(
        amount,
        date,
    ))

    # You might also want to see how much a certain item yielded you recently.
    typeName = "Expanded Cargohold II"  # change this to something you sold.
    amount = 0.0
    date = 0

    wallet = rich_char.WalletTransactions()
    try:
        soldTx = wallet.transactions.GroupedBy("transactionType")["sell"]
        for row in soldTx.GroupedBy("typeName")[typeName]:
            amount += (row.quantity * row.price)
            date = row.transactionDateTime
            assert isinstance(date, datetime)
    except KeyError:  # has not sold any
        pass

    print("{} sales yielded {:,.2f} ISK since {}".format(
        typeName,
        amount,
        date,
    ))

    # this isn't really a test. but it does a bunch of stuff that can error
