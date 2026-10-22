"""CLI utama UTS Praktikum Penelusuran Informasi."""

from ir_system import MultiDatasetIR


def print_menu() -> None:
    print("\n=== INFORMATION RETRIEVAL SYSTEM ===")
    print("[1] Load & Index Dataset")
    print("[2] Search Query")
    print("[3] Exit")
    print("====================================")


def show_results(system: MultiDatasetIR, results) -> None:
    if not results:
        print("\nTidak ada dokumen relevan yang ditemukan.")
        return

    print("\n=== TOP 5 HASIL PENCARIAN ===")
    for item in results:
        print(f"\n[{item.rank}] {item.title}")
        print(f"    Dataset : {item.source}")
        print(f"    Cosine  : {item.score:.4f}")
        print(f"    Cuplikan: {system.snippet(item.content)}")
    print("\n================================")


def main() -> None:
    system = MultiDatasetIR()

    while True:
        print_menu()
        choice = input("Pilih menu [1-3]: ").strip()

        if choice == "1":
            try:
                print("\nMemuat, melakukan preprocessing, dan membentuk Whoosh index...")
                total = system.build_index(recreate=True)
                print(f"\nSelesai. {total:,} dokumen berhasil di-index.")
                print("Ringkasan dataset:")
                print(system.dataset_summary().to_string(index=False))
            except Exception as exc:
                print(f"\nGagal membangun index: {exc}")

        elif choice == "2":
            query = input("\nMasukkan query: ").strip()
            if not query:
                print("Query tidak boleh kosong.")
                continue
            try:
                results = system.search(query, top_k=5, candidate_limit=100)
                show_results(system, results)
            except Exception as exc:
                print(f"\nPencarian gagal: {exc}")

        elif choice == "3":
            print("Program selesai. Terima kasih.")
            break

        else:
            print("Pilihan tidak valid. Masukkan 1, 2, atau 3.")


if __name__ == "__main__":
    main()
