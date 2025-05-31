def get_client_ip(request):
    """
    Returns the best estimate of the client's IP address.
    Takes into account proxies (X-Forwarded-For) while avoiding misuse.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_list = [ip.strip() for ip in x_forwarded_for.split(',')]
        # Take the first public IP (to avoid internal IPs)
        for ip in ip_list:
            if not ip.startswith(('10.', '192.168.', '172.', '127.')):
                return ip
        return ip_list[0]  # fallback if no public IP found
    return request.META.get('REMOTE_ADDR')
