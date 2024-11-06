<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Virtual Machines</h1>
        <hr><br><br>
        <button
        type="button"
        class="btn btn-success btn-sm"
        @click="toggleAddBookModal">
        Add VM
        </button>
        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Status</th>
              <th scope="col">?</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(book, index) in books" :key="index">
              <td>{{ book.name}}</td>
              <td>{{ book.status}}</td>
              <td>
                <span v-if="book.read">Yes</span>
                <span v-else>No</span>
              </td>
              <td>
                <div class="btn-group" role="group">
                  <button type="button" class="btn btn-warning btn-sm">Update</button>
                  <button type="button" class="btn btn-danger btn-sm">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

<!-- add new book modal -->
<div
ref="addBookModal"
class="modal fade"
:class="{ show: activeAddBookModal, 'd-block': activeAddBookModal }"
tabindex="-1"
role="dialog">
<div class="modal-dialog" role="document">
  <div class="modal-content">
    <div class="modal-header">
      <h5 class="modal-title">Add a new VM</h5>
      <button
        type="button"
        class="close"
        data-dismiss="modal"
        aria-label="Close"
        @click="toggleAddBookModal">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
    <div class="modal-body">
      <form>
        <div class="mb-3">
          <label for="addVMName" class="form-label">Name:</label>
          <input
            type="text"
            class="form-control"
            id="addVMName"
            v-model="addVMForm.name"
            placeholder="Enter name of the VM">
        </div>
        <div class="mb-3">
          <label for="addVMCPU" class="form-label">CPUs:</label>
          <input
            type="text"
            class="form-control"
            id="addVMCPU"
            v-model="addVMForm.cpu"
            placeholder="Enter number of CPUs">
        </div>
        <div class="mb-3">
          <label for="addVMRAM" class="form-label">RAM:</label>
          <input
            type="text"
            class="form-control"
            id="addVMRAM"
            v-model="addVMForm.ram"
            placeholder="Enter RAM (MB)">
        </div>
        
        <div class="btn-group" role="group">
          <button
            type="button"
            class="btn btn-primary btn-sm"
            @click="handleAddSubmit">
            Submit
          </button>
          <button
            type="button"
            class="btn btn-danger btn-sm"
            @click="handleAddReset">
            Reset
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
</div>
<div v-if="activeAddBookModal" class="modal-backdrop fade show"></div>

  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      activeAddBookModal: false,
      addVMForm: {
        name: '',
        cpu: '',
        ram: '',
      },
      books: [],
    };
  },
  methods: {
    addBook(payload) {
      const path = 'http://localhost:5000/books';
      axios.post(path, payload)
        .then(() => {
          this.getBooks();
        })
        .catch((error) => {

          console.log(error);
          this.getBooks();
        });
    },
    getBooks() {
      const path = 'http://localhost:5000/books';
      axios.get(path)
        .then((res) => {
          this.books = res.data.books;
        })
        .catch((error) => {

          console.error(error);
        });
    },
    handleAddReset() {
      this.initForm();
    },
    handleAddSubmit() {
      this.toggleAddBookModal();
      // let read = false;
      // if (this.addVMForm.read[0]) {
      //   read = true;
      // }
      const payload = {
        name: this.addVMForm.name,
        cpu: this.addVMForm.cpu,
        ram: this.addVMForm.ram,
      };
      this.addBook(payload);
      this.initForm();
    },
    initForm() {
      this.addVMForm.name = '';
      this.addVMForm.cpu = '';
      this.addVMForm.ram = '';
    },
    toggleAddBookModal() {
      const body = document.querySelector('body');
      this.activeAddBookModal = !this.activeAddBookModal;
      if (this.activeAddBookModal) {
        body.classList.add('modal-open');
      } else {
        body.classList.remove('modal-open');
      }
    },
  },
  created() {
    this.getBooks();
  },
};
</script>



