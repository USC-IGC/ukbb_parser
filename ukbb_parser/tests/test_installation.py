def main():
    try:
        import ukbb_parser.scripts.demo_conversion as dc
    except ImportError:
        from ukbb_parser.ukbb_parser import scripts
        print(scripts.__file__)

if __name__ == "__main__":
    main()
