"""
Neljän inputin kombinaatiot, output tuple
input: username file content | password file content | username input | password input
output: ()

Molemmat filut annettu - lue filuista
input: "cred=UKKELI" | "cred=SALASANA" | None | None
output: ("UKKELI", "SALASANA")

Username filua ei annettu - kysy input
input: None | "cred=SALASANA" | "UKKELI" | "SALASANA"
output: ("UKKELI", "SALASANA")

Salasana filua ei annettu - kysy input
input: "cred=UKKELI" | None | "UKKELI" | "SALASANA"
output: ("UKKELI", "SALASANA")

Kumpaakaan filua ei annettu - kysy input
input: None | None | "UKKELI" | "SALASANA"
output: ("UKKELI", "SALASANA")

WA filuista - palauttaa tyhjän merkkijonon
input: "cred=" | "cred=" | None | None
output: ("", "")

WA inputista - palauttaa tyhjän merkkijonon
input: None | None | "" | ""
output: ("", "")

Filut annettu parametreina, mutta ei olemassa - kysy input
input: <param given but file doesn't exist> | <param given but file doesn't exist> | "UKKELI" | "SALASANA"
output: ("UKKELI", "SALASANA")

"""
import ahjo.credential_handler as ahjo

def setup_function(tmp_path, usrn_file_content, pw_file_content):
    """ setup any state tied to the execution of the given function.
    Invoked for every test function in the module.
    """
    # username file
    usrn_file_path = None
    if usrn_file_content:
        usrn_file = tmp_path / "usrn.txt"
        usrn_file_path = usrn_file
        if usrn_file_content != 'broken_file':
            usrn_file.write_text(usrn_file_content)
    # password file
    pw_file_path = None
    if pw_file_content:
        pw_file = tmp_path / "pw.txt"
        pw_file_path = pw_file
        if pw_file_content != 'broken_file':
            pw_file.write_text(pw_file_content)
    return usrn_file_path, pw_file_path


def teardown_function(tmp_path):
    """ teardown any state that was previously setup with a setup_function
    call."""
    # poista luodut tiedostot

def test_function():
    print('Testi')


@pytest.fixture
def execute_get_credentials_with_varying_input(tmp_path):

    created_records = []

    def get_credentials(input):
        # username file
        usrn_file_path = None
        if usrn_file_content:
            usrn_file = tmp_path / "usrn.txt"
            usrn_file_path = usrn_file
            if usrn_file_content != 'broken_file':
                usrn_file.write_text(usrn_file_content)
        # password file
        pw_file_path = None
        if pw_file_content:
            pw_file = tmp_path / "pw.txt"
            pw_file_path = pw_file
            if pw_file_content != 'broken_file':
                pw_file.write_text(pw_file_content)
        return ahjo.get_credentials(usrn_file_path=usrn_file_path, pw_file_path=pw_file_path)

    yield get_credentials

    for record in created_records:
        record.destroy()

    

#def execute_get_credentials(usrn_file_path, pw_file_path):
#    # kirjoita tiedostot ja aseta input
#    return ahjo.get_credentials(usrn_file_path=usrn_file_path, pw_file_path=pw_file_path)
#
#def execute_get_credentials_with_varying_input():
#    setup_function()
#    execute_get_credentials()
#    teardown_function()
#
#def test_credentials_should_be_read_from_file_when_both_paths_given():
#    {"usrn_file_content": "cred=UKKELI", "cred=SALASANA", None, None}
#    assert ("UKKELI", "SALASANA") == execute_get_credentials_with_varying_input(testinput)
#
#
#def test_credentials_should_be_asked_when_username_file_not_given():
#    testinput = (None, "cred=SALASANA", "UKKELI", "SALASANA")
#    assert ("UKKELI", "SALASANA") == execute_get_credentials_with_varying_input(testinput)
