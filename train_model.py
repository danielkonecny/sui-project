from model import Model


def main():
    epoch_count = 10

    model = Model()
    model.train(epoch_count)
    model.save()


if __name__ == '__main__':
    main()
