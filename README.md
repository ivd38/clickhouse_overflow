Clickhouse heap overflow

No authentication is required to trigger this bug.

```

$ echo 'SELECT version()' | curl 'http://localhost:8123/?user=test&password=1234' -d @-
22.8.1.1

bool HTTPChunkedReadBuffer::nextImpl()
{
    if (!in)
        return false;

    /// The footer of previous chunk.
    if (count())
        readChunkFooter();

[1]    size_t chunk_size = readChunkHeader();
    if (0 == chunk_size)
    {
        readChunkFooter();
        in.reset();  // prevent double-eof situation.
        return false;
    }

 if (in->available() >= chunk_size)
    {
        /// Zero-copy read from input.
        working_buffer = Buffer(in->position(), in->position() + chunk_size);
        in->position() += chunk_size;
    }
    else
    {
        /// Chunk is not completely in buffer, copy it to scratch space.
[2]        memory.resize(chunk_size);
[3]        in->readStrict(memory.data(), chunk_size);
        working_buffer = Buffer(memory.data(), memory.data() + chunk_size);
    }
   ...
}

From ./src/IO/BufferWithOwnMemory.h
void resize(size_t new_size)
    {
        if (0 == m_capacity)
        {
            m_size = new_size;
            m_capacity = new_size;
            alloc();
        }
        else if (new_size <= m_capacity - pad_right)
        {
            m_size = new_size;
            return;
        }
        else
        {
[4]            size_t new_capacity = align(new_size, alignment) + pad_right;

            size_t diff = new_capacity - m_capacity;
            ProfileEvents::increment(ProfileEvents::IOBufferAllocBytes, diff);

            m_data = static_cast<char *>(Allocator::realloc(m_data, m_capacity, new_capacity, alignment));
            m_capacity = new_capacity;
            m_size = m_capacity - pad_right;
        }
    }

```

readChunkHeader() does not have any limits on line #1, so we can set chunk_size to (size_t)-1.

On line #2 resize() have an integer overflow (see line #4, pad_right = 15, alignment = 0), 
as a result small buffer will be allocated.

On line #3 it leads to heap overflow.

How to test:
```
$ ./t1.py
```
