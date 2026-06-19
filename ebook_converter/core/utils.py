import os


def get_file_extension(file_path: str) -> str:
    return os.path.splitext(file_path)[1].lower().lstrip('.')


def get_format_from_extension(ext: str) -> str:
    mapping = {
        'epub': 'epub',
        'mobi': 'mobi',
        'azw3': 'mobi',
        'azw': 'mobi',
        'prc': 'mobi',
        'txt': 'txt',
        'text': 'txt',
        'pdf': 'pdf',
        'md': 'md',
        'markdown': 'md',
    }
    return mapping.get(ext.lower(), '')


def get_output_extension(fmt: str) -> str:
    mapping = {
        'epub': '.epub',
        'mobi': '.mobi',
        'txt': '.txt',
        'pdf': '.pdf',
        'md': '.md',
    }
    return mapping.get(fmt.lower(), '.txt')


def output_path_for(input_path: str, target_format: str, output_dir: str = None) -> str:
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    ext = get_output_extension(target_format)
    out_name = base_name + ext
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, out_name)
    return os.path.join(os.path.dirname(input_path), out_name)
