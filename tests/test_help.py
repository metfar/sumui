from sumui import HelpCorpus, HelpTopic;


def topic(name, category="General", example="example()"):
    return HelpTopic(name, category, "summary", ("{}()".format(name),), example);


def test_help_topics_are_global_alphabetical():
    corpus = HelpCorpus("Test", [topic("ZETA", "A"), topic("ALPHA", "Z"), topic("MID", "A")]);
    assert corpus.topic_names() == ["ALPHA", "MID", "ZETA"];


def test_help_topic_requires_example():
    try:
        topic("BROKEN", example="");
    except ValueError as error:
        assert "requires a functional example" in str(error);
    else:
        raise AssertionError("HelpTopic accepted an empty example");


def test_alias_resolution_is_backend_neutral():
    item = HelpTopic("VLOOKUP", "Lookup", "summary", ("VLOOKUP(...)" ,), "VLOOKUP(1, table, 2)", aliases=("BUSCARV",));
    corpus = HelpCorpus("Functions", [item]);
    assert corpus.find_topic("BUSCARV") is item;
