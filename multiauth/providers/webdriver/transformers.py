from selenium.webdriver.common.by import By


def target_to_selector(target: str) -> str:
    if target == 'name':
        return By.NAME
    if target == 'css:finder':
        return By.CSS_SELECTOR
    if target.startswith('xpath'):
        return By.XPATH

    raise Exception(f'Invalid target `{target}`')


def target_to_value(target: str) -> str:
    return target.split('=')[1]


def target_to_selector_value(target_pair: list[str]) -> tuple[str, str]:
    return target_to_selector(target_pair[1]), target_to_value(target_pair[0])
