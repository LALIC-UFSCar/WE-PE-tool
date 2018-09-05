class BlastReader(object):

    def __init__(self, filename):
        self.error_lines = list()
        self.src_lines = list()
        self.ref_lines = list()
        self.sys_lines = list()

        with open(filename, 'r') as blast_file:
            blast_file.readline()
            blast_file.readline()

            line = 0

            while True:
                src = blast_file.readline().split()
                if not src:
                    break

                self.src_lines.append(src)
                self.ref_lines.append(blast_file.readline().split())
                self.sys_lines.append(blast_file.readline().split())
                blast_file.readline()
                errors = [e.split('#') for e in blast_file.readline().split()]

                for error in errors:
                    error_indexes = [list(map(int, e.split(',')))
                                     for e in error[:-1]]
                    error_indexes.append(error[-1])
                    self.error_lines.append((line, error_indexes))

                line = line + 1

    def get_filtered_errors(self, tags):
        return [e for e in self.error_lines if e[1][-1] in tags]

    def get_incorrect_words(self, errors):
        """Get all incorrect words aligned by annotation

        Arguments:
            errors {list} -- Error types

        Returns:
            list -- List of triples of aligned words for each error occurrence
        """

        words = list()

        for error in errors:
            line = error[0]

            src_words = [self.src_lines[line][i] for i in error[1][0] if i > 0]
            sys_words = [self.sys_lines[line][i] for i in error[1][1] if i > 0]
            ref_words = [self.ref_lines[line][i] for i in error[1][2] if i > 0]

            words.append((src_words, ref_words, sys_words))

        return words

    def get_correct_indices(self):
        """Return all line indices which contain no error

        Returns:
            list -- List of numbers, which indicate with lines have
                    no error referring to it
        """

        num_lines = len(self.src_lines)
        error_indices = [l for (l, _) in self.error_lines]
        correct_indices = list()

        for i in range(num_lines):
            if i not in error_indices:
                correct_indices.append(i)

        return correct_indices

    def get_error_messages(self, line):
        """Returns all errors associated to a given line index

        Arguments:
            line {int} -- Line number

        Returns:
            list -- All errors (indexes and error type) associated to the given line
        """

        return [error[1] for error in self.error_lines if line == error[0]]
