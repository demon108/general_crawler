from mxutil import is_post_page,is_list_page

def bbs_rule(src_url,sites,depth):
    rule_sites = []
    is_post_p = is_post_page(src_url)
    is_list_p = is_list_page(src_url)
    for t_str in sites:
        _depth = depth

        if depth == "1":
            if is_post_page(t_str) or is_list_page(t_str):
                _depth = depth
            else:
                _depth = "2" #get the other type to next page
        elif depth == "2":
            if is_list_p:
                if is_post_page(t_str) or is_list_page(t_str):
                    _depth = depth
                else:
                    continue
            elif is_post_p:
                if not is_post_page(t_str):
                    continue
            else:
                continue
        elif depth == "3":
            if is_post_p:
                continue
            elif is_list_p:
                if not is_post_page(t_str):
                    continue
        else:
            continue
        
        rule_sites.append(t_str)
    
    return rule_sites
